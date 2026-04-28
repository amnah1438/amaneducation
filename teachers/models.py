from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

class Teacher(models.Model):
user = models.OneToOneField(
User, on_delete=models.CASCADE,
related_name=“teacher”, verbose_name=“حساب المستخدم”
)
full_name = models.CharField(max_length=200, verbose_name=“اسم المعلمة”)

```
class Meta:
    verbose_name = "معلمة"
    verbose_name_plural = "المعلمات"
    ordering = ["full_name"]

def __str__(self):
    return self.full_name
```

class TeacherSkill(models.Model):
CONTENT_TYPE = [
(‘skill’, ‘مهارة قدرات’),
(‘lesson’, ‘درس تحصيلي’),
(‘bank’, ‘بنك أسئلة’),
(‘comprehensive’, ‘اختبار شامل’),
]
TYPE_CHOICES = [
(‘qodrat_kamy’, ‘قدرات — كمي’),
(‘qodrat_lafzy’, ‘قدرات — لفظي’),
]
SUBJECT_CHOICES = [
(‘math’, ‘تحصيلي — رياضيات’),
(‘bio’, ‘تحصيلي — أحياء’),
(‘chem’, ‘تحصيلي — كيمياء’),
(‘phys’, ‘تحصيلي — فيزياء’),
]

```
content_type = models.CharField(max_length=20, choices=CONTENT_TYPE, default='skill', verbose_name="نوع المحتوى")
title = models.CharField(max_length=200, verbose_name="العنوان")
skill_type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, verbose_name="نوع القدرات")
subject = models.CharField(max_length=10, choices=SUBJECT_CHOICES, blank=True, verbose_name="مادة التحصيلي")
description = models.TextField(blank=True, verbose_name="وصف مختصر")
created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_skills", verbose_name="المعلمة المنشئة")
target_classes = models.CharField(max_length=100, blank=True, verbose_name="الفصول المستهدفة")
is_shared = models.BooleanField(default=True, verbose_name="مشاركة مع المعلمات")
is_active = models.BooleanField(default=False, verbose_name="مفعّلة")
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

class Meta:
    verbose_name = "مهارة / درس"
    verbose_name_plural = "المهارات والدروس"
    ordering = ["-created_at"]

def __str__(self):
    return f"{self.get_content_type_display()} — {self.title}"
```

class TeacherSkillContent(models.Model):
skill = models.OneToOneField(TeacherSkill, on_delete=models.CASCADE, related_name=“content”, verbose_name=“المهارة/الدرس”)
text_content = RichTextUploadingField(config_name=‘scientific_editor’, blank=True, null=True, verbose_name=“شرح نصي (مع رموز ومعادلات)”)
plain_text = models.TextField(blank=True, verbose_name=“شرح نصي بسيط”)
plain_image = models.ImageField(upload_to=‘skill_content/’, blank=True, null=True, verbose_name=“صورة توضيحية”)
video_url = models.URLField(blank=True, verbose_name=“رابط فيديو”)
pdf_file = models.FileField(upload_to=‘skill_pdfs/’, blank=True, null=True, verbose_name=“ملف PDF”)

```
class Meta:
    verbose_name = "محتوى الشرح"
    verbose_name_plural = "محتوى الشروح"

def __str__(self):
    return f"شرح — {self.skill.title}"
```

class TeacherExam(models.Model):
EXAM_TYPE = [
(‘pre’, ‘اختبار قبلي’),
(‘post’, ‘اختبار بعدي’),
(‘lesson’, ‘اختبار درس تحصيلي’),
(‘bank’, ‘اختبار من بنك الأسئلة’),
(‘comprehensive_qodrat’, ‘اختبار شامل — قدرات’),
(‘comprehensive_tahsili’, ‘اختبار شامل — تحصيلي’),
]
DELIVERY_TYPE = [
(‘electronic’, ‘إلكتروني فقط’),
(‘paper’, ‘ورقي فقط’),
(‘both’, ‘إلكتروني + ورقي’),
]
CORRECTION_TYPE = [
(‘auto’, ‘تلقائي’),
(‘manual’, ‘يدوي’),
(‘both’, ‘كلاهما’),
]

```
skill = models.ForeignKey(TeacherSkill, on_delete=models.CASCADE, related_name="exams", verbose_name="المهارة/الدرس")
exam_type = models.CharField(max_length=30, choices=EXAM_TYPE, verbose_name="نوع الاختبار")
questions_count = models.PositiveIntegerField(default=10, verbose_name="عدد الأسئلة")
duration_minutes = models.PositiveIntegerField(default=15, verbose_name="مدة الاختبار (دقيقة)")
pass_score = models.PositiveIntegerField(default=60, verbose_name="درجة النجاح %")
start_date = models.DateField(blank=True, null=True, verbose_name="تاريخ البدء")
end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الانتهاء")
delivery = models.CharField(max_length=15, choices=DELIVERY_TYPE, default='both', verbose_name="طريقة التسليم")
correction = models.CharField(max_length=10, choices=CORRECTION_TYPE, default='auto', verbose_name="طريقة التصحيح")
is_active = models.BooleanField(default=False, verbose_name="مفعّل")
shuffle_questions = models.BooleanField(default=True, verbose_name="ترتيب عشوائي")
created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    verbose_name = "اختبار"
    verbose_name_plural = "الاختبارات"

def __str__(self):
    return f"{self.get_exam_type_display()} — {self.skill.title}"
```

class TeacherQuestion(models.Model):
CORRECT_CHOICES = [
(‘A’, ‘أ’), (‘B’, ‘ب’), (‘C’, ‘ج’), (‘D’, ‘د’),
]

```
exam = models.ForeignKey(TeacherExam, on_delete=models.CASCADE, related_name="questions", verbose_name="الاختبار")
target_skill_name = models.CharField(max_length=200, blank=True, verbose_name="المهارة المستهدفة")
order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")

question_text = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="نص السؤال (مع رموز)")
option_a = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="خيار أ")
option_b = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="خيار ب")
option_c = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="خيار ج")
option_d = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="خيار د")
feedback = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="تغذية راجعة")

question_plain = models.TextField(blank=True, verbose_name="نص السؤال البسيط")
question_image = models.ImageField(upload_to='questions/', blank=True, null=True, verbose_name="صورة السؤال")
option_a_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار أ (نص)")
option_b_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار ب (نص)")
option_c_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار ج (نص)")
option_d_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار د (نص)")
feedback_plain = models.TextField(blank=True, verbose_name="تغذية راجعة بسيطة")

correct_answer = models.CharField(max_length=1, choices=CORRECT_CHOICES, verbose_name="الإجابة الصحيحة")

class Meta:
    verbose_name = "سؤال"
    verbose_name_plural = "الأسئلة"
    ordering = ["order"]

def __str__(self):
    from django.utils.html import strip_tags
    text = strip_tags(self.question_text or self.question_plain or "")
    return f"س{self.order} — {text[:50]}"
```

class ExamResult(models.Model):
exam = models.ForeignKey(TeacherExam, on_delete=models.CASCADE, related_name=“results”, verbose_name=“الاختبار”)
student = models.ForeignKey(User, on_delete=models.CASCADE, related_name=“teacher_exam_results”, verbose_name=“الطالبة”)
score = models.FloatField(default=0, verbose_name=“الدرجة”)
total = models.PositiveIntegerField(default=10, verbose_name=“الدرجة الكاملة”)
percentage = models.FloatField(default=0, verbose_name=“النسبة %”)
passed = models.BooleanField(default=False, verbose_name=“ناجحة”)
time_taken_seconds = models.PositiveIntegerField(default=0, verbose_name=“الوقت المستغرق (ثانية)”)
manually_corrected = models.BooleanField(default=False, verbose_name=“صُحّح يدوياً”)
corrected_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name=“corrected_results”, verbose_name=“صحّحتها”)
submitted_at = models.DateTimeField(auto_now_add=True)

```
class Meta:
    verbose_name = "نتيجة اختبار"
    verbose_name_plural = "نتائج الاختبارات"
    unique_together = ['exam', 'student']

def __str__(self):
    return f"{self.student.username} — {self.exam} — {self.score}/{self.total}"
```

class StudentAnswer(models.Model):
result = models.ForeignKey(ExamResult, on_delete=models.CASCADE, related_name=“answers”, verbose_name=“النتيجة”)
question = models.ForeignKey(TeacherQuestion, on_delete=models.CASCADE, verbose_name=“السؤال”)
chosen_answer = models.CharField(max_length=1, verbose_name=“الإجابة المختارة”)
is_correct = models.BooleanField(default=False, verbose_name=“صحيحة”)

```
class Meta:
    verbose_name = "إجابة طالبة"
    verbose_name_plural = "إجابات الطالبات"

def __str__(self):
    return f"{self.result.student.username} — س{self.question.order} — {'✓' if self.is_correct else '✗'}"
```

class ClassSession(models.Model):
SESSION_TYPE = [
(‘qodrat’, ‘قدرات’),
(‘tahsili’, ‘تحصيلي’),
(‘both’, ‘قدرات + تحصيلي’),
]

```
teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="sessions", verbose_name="المعلمة")
skill = models.ForeignKey(TeacherSkill, on_delete=models.CASCADE, related_name="sessions", verbose_name="المهارة/الدرس")
exam = models.ForeignKey(TeacherExam, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions", verbose_name="الاختبار المفعّل")
session_type = models.CharField(max_length=10, choices=SESSION_TYPE, default='qodrat', verbose_name="نوع الحصة")
target_class = models.CharField(max_length=50, verbose_name="الفصل المستهدف")
session_date = models.DateField(verbose_name="تاريخ الحصة")
session_time = models.TimeField(verbose_name="وقت الحصة")
notes = models.TextField(blank=True, verbose_name="ملاحظات")
created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    verbose_name = "سجل حصة"
    verbose_name_plural = "سجل الحصص"
    ordering = ["-session_date", "-session_time"]

def __str__(self):
    return f"{self.teacher.full_name} — {self.skill.title} — {self.session_date}"
```