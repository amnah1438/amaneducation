from django.db import models


class ClassRoom(models.Model):
    name = models.CharField(max_length=100)  # مثل: ثالث ثانوي (1)

    def __str__(self):
        return self.name


class Student(models.Model):
    full_name = models.CharField(max_length=200)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="students")

    def __str__(self):
        return self.full_name
