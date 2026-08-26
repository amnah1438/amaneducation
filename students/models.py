from django.db import models


class ClassRoom(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="اسم الفصل"
    )  # مثل: ثالث ثانوي (1)

    class Meta:
        verbose_name = "فصل"
        verbose_name_plural = "الفصول"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    full_name = models.CharField(
        max_length=200,
        verbose_name="اسم الطالبة"
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="الفصل"
    )

    class Meta:
        verbose_name = "طالبة"
        verbose_name_plural = "الطالبات"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class RemedialExamAssignment(models.Model):
    """تعيين اختبار علاجي لطالبة محددة من قبل المعلمة."""
    exam_id = models.IntegerField(verbose_name="معرّف الاختبار")
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="remedial_assignments",
        verbose_name="الطالبة"
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التعيين")

    class Meta:
        verbose_name = "تعيين اختبار علاجي"
        verbose_name_plural = "تعيينات الاختبارات العلاجية"
        ordering = ["-assigned_at"]
        unique_together = [("exam_id", "student")]

    def __str__(self):
        return f"اختبار {self.exam_id} → {self.student.full_name}"
