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
