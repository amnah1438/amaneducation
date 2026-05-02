from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0005_alter_teacherexam_exam_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherquestion',
            name='option_a_image',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='questions/options/',
                verbose_name='صورة خيار أ',
            ),
        ),
        migrations.AddField(
            model_name='teacherquestion',
            name='option_b_image',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='questions/options/',
                verbose_name='صورة خيار ب',
            ),
        ),
        migrations.AddField(
            model_name='teacherquestion',
            name='option_c_image',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='questions/options/',
                verbose_name='صورة خيار ج',
            ),
        ),
        migrations.AddField(
            model_name='teacherquestion',
            name='option_d_image',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='questions/options/',
                verbose_name='صورة خيار د',
            ),
        ),
    ]
