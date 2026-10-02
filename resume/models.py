import os
import re

from django.contrib.auth.models import User
from django.db import models


def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user.id}/{filename}"


SECTION_HEADER_PATTERN = re.compile(r'^[A-Z][A-Z\s&/\-]{2,40}$')


class Resume(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="resume"
    )

    file = models.FileField(upload_to=resume_upload_path)

    original_filename = models.CharField(max_length=255, blank=True)

    extracted_text = models.TextField(blank=True)

    detected_skills = models.ManyToManyField(
        "skills.Skill", blank=True, related_name="resumes"
    )

    projects_text = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s resume"

    # ---------- raw text extraction ----------

    def extract_text(self):
        """
        Reads the uploaded file and returns its raw text.
        Returns an empty string if nothing could be extracted —
        never guesses or fabricates content.
        """
        ext = os.path.splitext(self.file.name)[1].lower()

        try:
            if ext == ".pdf":
                return self._extract_pdf_text()
            elif ext == ".docx":
                return self._extract_docx_text()
        except Exception:
            return ""

        return ""

    def _extract_pdf_text(self):
        import pdfplumber

        text_parts = []
        self.file.open("rb")
        with pdfplumber.open(self.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        self.file.close()

        return "\n".join(text_parts).strip()

    def _extract_docx_text(self):
        import docx

        self.file.open("rb")
        document = docx.Document(self.file)
        self.file.close()

        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()

    # ---------- structured parsing (best-effort) ----------

    def get_sections(self):
        """
        Splits extracted_text into sections using all-caps header lines
        (e.g. "SKILLS", "PROJECTS", "EDUCATION") as section boundaries.
        Best-effort only — resume formats vary widely, so this may not
        catch every section correctly.
        """
        sections = {}
        current_header = None
        current_lines = []

        for line in self.extracted_text.splitlines():
            stripped = line.strip()
            if (
                stripped
                and SECTION_HEADER_PATTERN.match(stripped)
                and len(stripped.split()) <= 6
            ):
                if current_header:
                    sections[current_header] = "\n".join(current_lines).strip()
                current_header = stripped
                current_lines = []
            else:
                current_lines.append(line)

        if current_header:
            sections[current_header] = "\n".join(current_lines).strip()

        return sections

    def parse_projects_text(self):
        """
        Returns the text of whichever section header contains the word
        PROJECT (e.g. "PROJECTS", "SOFTWARE DEVELOPMENT PROJECTS").
        Returns "" if no such section was found — never invents one.
        """
        for header, text in self.get_sections().items():
            if "PROJECT" in header:
                return text
        return ""

    def parse_project_blocks(self):
        """
        Splits projects_text into individual project blocks.
        Assumes each project starts with a line containing a comma-
        separated tech list after a name, e.g. "Project Name , Python | MySQL".
        Best-effort only — returns [] if nothing could be split confidently.
        """
        text = self.projects_text
        if not text:
            return []

        lines = [l for l in text.splitlines() if l.strip()]
        blocks = []
        current_title = None
        current_tech = ""
        current_desc_lines = []

        title_line_pattern = re.compile(r'^(.+?)\s*,\s*(.+\|.+)$')

        for line in lines:
            stripped = line.strip()
            if stripped == "•":
                continue

            match = title_line_pattern.match(stripped)
            if match:
                if current_title:
                    blocks.append({
                        "title": current_title,
                        "technologies": current_tech,
                        "description": " ".join(current_desc_lines).strip(),
                    })
                current_title = match.group(1).strip()
                current_tech = match.group(2).replace("|", ",").strip()
                current_desc_lines = []
            else:
                current_desc_lines.append(stripped)

        if current_title:
            blocks.append({
                "title": current_title,
                "technologies": current_tech,
                "description": " ".join(current_desc_lines).strip(),
            })

        return blocks

    def parse_matched_skills(self):
        """
        Returns Skill objects whose exact name appears as a whole word
        in the resume text. Only matches skills that already exist in
        the Skill table — never invents a new skill.
        """
        from skills.models import Skill

        text_lower = self.extracted_text.lower()
        matched = []

        for skill in Skill.objects.all():
            pattern = r'\b' + re.escape(skill.name.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched.append(skill)

        return matched