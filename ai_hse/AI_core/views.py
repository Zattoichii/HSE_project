import os
from dotenv import load_dotenv

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from openai import OpenAI

from .models import CustomUser


User = get_user_model()

load_dotenv()
Groq_token = os.getenv('GROQ_TOKEN')

def custom_404(request, exception):
    return render(request, "404.html", status=404)

class CustomLoginView(LoginView):
    template_name = "login.html"


def registration_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = CustomUser.objects.create_user(
            username=email,  
            email=email,
            password=password
        )

        login(request, user)

        return redirect("main_page")

    return render(request, "registration.html")


@login_required
def main_page(request):
    generated_text = None
    show_payment = False
    user = request.user

    if request.method == "POST":
        if user.request_count >= user.max_requests:
            show_payment = True
        else:
            TA_age = request.POST.get("TA_age")
            TA_income = request.POST.get("TA_income")
            TA_interests = request.POST.get("TA_interests")
            TA_social_status = request.POST.get("TA_social_status")
            TA_gender = request.POST.get("TA_gender")
            TA_education = request.POST.get("TA_education")
            communication_type = request.POST.get("communication_type")
            communication_purpose = request.POST.get("communication_purpose")
            extra_info = request.POST.get("extra_info")
            user_name = request.POST.get("user_name")

            promt = f'''
            Ты — опытный копирайтер и CRM-специалист с более чем 10-летним опытом в крупной компании. Ты эксперт и мастерски создаешь персонализированные, цепляющие и конверсионные тексты для разных каналов коммуникации. Ты отлично знаешь психологию потребителя, умеешь работать с целевой аудиторией и адаптировать тон, длину и призыв к действию под конкретный канал.
            Задача: Напиши текст для маркетинговой коммуникации на основе предоставленных данных.
            Входные данные:
            Тип коммуникации: {communication_type}
            Цель коммуникации, что хотим сказать пользователю: {communication_purpose}
            Целевая аудитория (Target Audience):
            Возраст: {TA_age}
            Пол: {TA_gender}
            Доход: {TA_income}
            Интересы: {TA_interests}
            Социальный статус: {TA_social_status}
            Образование: {TA_education}
            Дополнительная информация о пользователе: {extra_info}
            Имя: {user_name}

            Важные инструкции:
            Если тип коммуникации Push уведомления: короткие и ясные. До 70 символов, можно использовать эмодзи. Должен быть цепляющий заголовок. 
            Если тип коммуникации СМС рассылка: короткие и ясные. До 70 символов, без эмодзи. Более строгий стиль общения.
            Если тип коммуникации Email рассылка: до 300 символов, без эмодзи 
            Адаптация под канал: Учти особенности канала коммуникации.
            Работа с данными ЦА: Тщательно проанализируй предоставленные данные о целевой аудитории. Используй их для тона, аргументации и выбора бенефитов.
            Если какой-либо параметр ЦА отсутствует или не указан, сделай текст более универсальным, сфокусировавшись на цели коммуникации и базовых триггерах (выгода, ограниченность предложения, любопытство).
            Структура и элементы:
            Заголовок: Цепляющий, интригующий или прямо говорящий о выгоде.
            Основной текст: Раскрывает ценность предложения для конкретной ЦА. 
            Призыв к действию (CTA): Четкий, понятный и побудительный (например, "Получить скидку", "Забрать товар", "Узнать первым").
            Дедлайн/Условие (если уместно): Создай ощущение срочности или эксклюзивности (например, "только до конца недели", "только для вас").
            Тон и стиль: Тон должен соответствовать ЦА. Для молодежи — более неформальный и динамичный, для старшей аудитории с высоким доходом — уважительный и сдержанный, подчеркивающий статус и качество.
            Формат вывода (Output Format):
            Предоставь ответ в виде чистого, готового к использованию текста. Не объясняй свои решения и не добавляй мета-комментарии. Просто выдай финальный текст, готовый к отправке. Не задавай уточняющих вопросов, работай только с представленной информацией. Не используй разметку markdown 
        '''

            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key="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"
            )

            response = client.responses.create(
                model="openai/gpt-oss-20b",
                input=promt
            )

            generated_text = response.output_text
            user.request_count += 1
            user.save()

    remaining_requests = max(user.max_requests - user.request_count, 0)

    return render(request, "main_page.html", {
        "result": generated_text,
        "show_payment": show_payment,
        "remaining_requests": remaining_requests
    })
