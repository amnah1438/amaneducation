from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemedialExamAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_id', models.IntegerField(verbose_name='معرّف الاختبار')),
                ('assigned_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التعيين')),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='remedial_assignments',
                    to='students.student',
                    verbose_name='الطالبة',
                )),
            ],
            options={
                'verbose_name': 'تعيين اختبار علاجي',
                'verbose_name_plural': 'تعيينات الاختبارات العلاجية',
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='remedialexamassignment',
            unique_together={('exam_id', 'student')},
        ),
    ]
