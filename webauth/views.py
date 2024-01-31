from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import View
# to activate the user accounts
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError

# getting token from utilis.py
from .utils import generate_tokens
from tokenize import generate_tokens
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# emails
from django.conf import settings
from django.core.mail import EmailMessage

# threading
import threading

class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()




        

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match. Please try again!")
            return redirect('auth/signup.html')  # Use the correct URL pattern

        try:
            if User.objects.get(username=email):
                messages.warning(request, "Email Already Exists")
                return redirect('auth/signup.html')  # Use the correct URL pattern
        except User.DoesNotExist:
            pass

        user = User.objects.create_user(email, email, pass1)
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        email_subject = "Activate Your Account"
        
        # Use the PasswordResetTokenGenerator for token generation
        token_generator = PasswordResetTokenGenerator()
        email_message = render_to_string('webauth/activate.html', {
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        })

        email = EmailMessage(email_subject, email_message, to=[email])
        threading.Thread(target=email.send).start()

        messages.info(request, "Activate Your Account by clicking the link in your email")
        return redirect('/webauth/login')  # Use the correct URL pattern

    return render(request, 'auth/signup.html')


class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try: 
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user =User.objects.get(pk=uid)
        
        except Exception as identifier:
            user = None

        if user is not None and generate_tokens.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/webauth/login') 
        
        return render(request, 'auth/activatefail.html')

def handlelogin(request):
    if request.method == 'POST':
        
        username = request.POST.get('email')
        userpassword = request.POST.get('pass1')
        user = authenticate(username=username, password=userpassword)

        if user is not None:
            login(request, user)
            messages.info(request, "Successfully Logged In")
            return render(request,'index.html')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/webauth/login')

    return render(request, 'auth/login.html')


def handlelogout(request):
    logout(request)
    messages.success(request, "Logout Success")
    return redirect('login')


class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'auth/request-reset-email.html')

    def post(self, request):
        email = request.POST['email']
        user = User.objects.filter(email=email)

        if user.exists():
            current_site = get_current_site(request)
            email_subject = 'Reset Your Password'
            message = render_to_string('auth/reset-user-password.html', {
                'domain': '127.0.0.1.8000',
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            })

            email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
            EmailThread(email_message).start()
            messages.info(request, "WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET THE PASSWORD")
            return render(request, 'auth/request-reset-email.html')
        else:
            messages.error(request, "Email not found. Please check the provided email address.")
            return render(request, 'auth/request-reset-email.html')

        
class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64' : uidb64,
            'token' : token,
        }
        try:
            user_id = force_bytes(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'auth/request-reset-email.html')
            
        except DjangoUnicodeDecodeError as identifier :
            pass

        return render(request,'auth/set-new-password.html',context)
    
    def post(self,request,uidb64,token):
        context={
            'uidb64': uidb64,
            'token' : token,
        }
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 != pass2:
            messages.warning(request, "Passwords do not match. Please try again!")
            return redirect('auth/set-new-password.html',context) 
        
        try:
            user_id = force_bytes(urlsafe_base64_decode(uidb64))
            user= User.objects.grt(pk=user_id)
            user.set_password(pass1)
            user.save()
            messages.success(request,"Password Reset Success Please Login with New Password")
            return redirect('/webauth/login/')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"Something Went Wrong")
            return render (request,'auth/set-new-password.html',context)
        
        return render(request,'auth/set-new-password.html',context)