# Generated manually to add new assessment models and update ProgramOutcome

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def delete_existing_program_outcomes(apps, schema_editor):
    """Delete existing ProgramOutcome records since they're linked to course instead of academic_board"""
    ProgramOutcome = apps.get_model('edupace_app', 'ProgramOutcome')
    ProgramOutcome.objects.all().delete()


def reverse_delete_program_outcomes(apps, schema_editor):
    """Reverse migration - nothing to do"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("edupace_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Delete existing ProgramOutcome records before changing the model structure
        migrations.RunPython(delete_existing_program_outcomes, reverse_delete_program_outcomes),
        # First, add academic_board field to ProgramOutcome (nullable temporarily)
        migrations.AddField(
            model_name="programoutcome",
            name="academic_board",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="program_outcomes",
                to="edupace_app.academicboard",
            ),
        ),
        # Create Assessment model
        migrations.CreateModel(
            name="Assessment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Assessment name (e.g., Midterm, Project, Final)",
                        max_length=100,
                    ),
                ),
                (
                    "weight_in_course",
                    models.FloatField(
                        help_text="Weight of this assessment in the course (0.0 to 1.0)",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assessments",
                        to="edupace_app.course",
                    ),
                ),
            ],
            options={
                "verbose_name": "Assessment",
                "verbose_name_plural": "Assessments",
                "ordering": ["course", "name"],
                "unique_together": {("course", "name")},
            },
        ),
        # Create AssessmentGrade model
        migrations.CreateModel(
            name="AssessmentGrade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "grade",
                    models.FloatField(
                        help_text="Grade as a percentage (0-100)",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(100.0),
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades",
                        to="edupace_app.assessment",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assessment_grades",
                        to="edupace_app.student",
                    ),
                ),
            ],
            options={
                "verbose_name": "Assessment Grade",
                "verbose_name_plural": "Assessment Grades",
                "ordering": ["assessment", "student"],
                "unique_together": {("assessment", "student")},
            },
        ),
        # Create AssessmentToLO model
        migrations.CreateModel(
            name="AssessmentToLO",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "weight",
                    models.FloatField(
                        help_text="Weight of this assessment in calculating the learning outcome score",
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lo_connections",
                        to="edupace_app.assessment",
                    ),
                ),
                (
                    "learning_outcome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assessment_connections",
                        to="edupace_app.learningoutcome",
                    ),
                ),
            ],
            options={
                "verbose_name": "Assessment to Learning Outcome",
                "verbose_name_plural": "Assessment to Learning Outcomes",
                "ordering": ["assessment", "learning_outcome"],
                "unique_together": {("assessment", "learning_outcome")},
            },
        ),
        # Create LOToPO model
        migrations.CreateModel(
            name="LOToPO",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "weight",
                    models.FloatField(
                        help_text="Weight of this learning outcome in calculating the program outcome score",
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "learning_outcome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="po_connections",
                        to="edupace_app.learningoutcome",
                    ),
                ),
                (
                    "program_outcome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lo_connections",
                        to="edupace_app.programoutcome",
                    ),
                ),
            ],
            options={
                "verbose_name": "Learning Outcome to Program Outcome",
                "verbose_name_plural": "Learning Outcome to Program Outcomes",
                "ordering": ["learning_outcome", "program_outcome"],
                "unique_together": {("learning_outcome", "program_outcome")},
            },
        ),
        # Update unique_together constraint first (before removing course field)
        migrations.AlterUniqueTogether(
            name="programoutcome",
            unique_together=set(),  # Remove old unique_together first
        ),
        # Remove course field from ProgramOutcome
        migrations.RemoveField(
            model_name="programoutcome",
            name="course",
        ),
        # Make academic_board non-nullable
        migrations.AlterField(
            model_name="programoutcome",
            name="academic_board",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="program_outcomes",
                to="edupace_app.academicboard",
            ),
        ),
        # Add new unique_together constraint
        migrations.AlterUniqueTogether(
            name="programoutcome",
            unique_together={("academic_board", "code")},
        ),
        # Update ordering
        migrations.AlterModelOptions(
            name="programoutcome",
            options={
                "ordering": ["academic_board", "code"],
                "verbose_name": "Program Outcome",
                "verbose_name_plural": "Program Outcomes",
            },
        ),
    ]

