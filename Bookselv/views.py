from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import File, Folder
from .forms import fileupform
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import os
import pdf2image
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404


def index(request, file_root):
    infolder = Folder.objects.filter(parent_folder_id = file_root).order_by('folder_name')
    infile = File.objects.filter(folder_root_id = file_root).order_by('filename')

    if Folder.objects.get(pk = file_root).parent_folder is not None:
        par = Folder.objects.get(pk = file_root).parent_folder.id
    else:
        par = 1;
    
    cont = {
        "infolder" : infolder, 
        "infile" : infile,
        "root" : file_root,
        "par" :  par
    }
    return render(request, 'online.html', cont)



def blink(request):
    return redirect('online/f/1')



def check_admin(user):
   return user.is_superuser


@user_passes_test(check_admin)
@login_required(login_url='loginadm')
def manage(request, file_root):
    infolder = Folder.objects.filter(parent_folder_id = file_root)
    infile = File.objects.filter(folder_root_id = file_root)
    allfold = Folder.objects.all()
    
    if Folder.objects.get(pk = file_root).parent_folder is not None:
        par = Folder.objects.get(pk = file_root).parent_folder.id
    else:
        par = 1;
    form = fileupform()

    cont = {
        "infolder" : infolder, 
        "infile" : infile,
        "root" : file_root,
        "form" : form,
        "par" : par,
        "allfold" : allfold
    }
    return render(request, 'manage.html', cont)


@login_required(login_url='loginusr')
def userpanel(request):
    if request.method == 'POST':
        uid = request.POST.get("uid")
        username = request.POST.get('username')
        email = request.POST.get('cemail')
        password = request.POST.get('cpass1')
        confirm_password = request.POST.get('cpass2')
        
        if not all([username, email, password, confirm_password]):
            messages.info(request, 'Please fill all fields')
            return redirect('userpanel')
        else: 
            if password == confirm_password:
                user = User.objects.get(pk=uid)

                if User.objects.filter(username=username).exclude(pk=uid).exists():
                    messages.info(request, 'Username taken')
                    return redirect('/userpanel/')

                elif User.objects.filter(email=email).exclude(pk=uid).exists():
                    messages.info(request, 'Email taken')
                    return redirect('/userpanel/')

                else:
                    user.username = username
                    user.email = email
                    user.set_password(password)
                    user.save()
                    messages.info(request, 'Edit successful')
                    login(request, user)
                    return redirect('/online/f/1')
            else:
                messages.info(request, 'Password does not match')
                return redirect('/userpanel/')
    else:
        return render(request, 'userpanel.html')


def loginusr(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/online/f/1')
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('loginusr')
    return render(request, 'login.html')



def loginadm(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/manage/f/1')
            else:
                messages.error(request, "There was an error logging in. Please try again.")
                return redirect('loginadm')    
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('loginadm')
    return render(request, 'login_adm.html')



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('cemail')
        password = request.POST.get('cpass1')
        confirm_password = request.POST.get('cpass2')
        
        if not all([username, email, password, confirm_password]):
            messages.info(request, 'Please Fill All FIeld')
            return redirect('register')
        else: 
            if password==confirm_password:
                if User.objects.filter(username=username).exists():
                    messages.info(request, 'Username Taken')
                    return redirect('register')
                elif User.objects.filter(email=email).exists():
                    messages.info(request, 'Email Taken')
                    return redirect('register')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, 'Register Successfull')
                    user.save()
                    return redirect('loginusr')
            else:
                messages.info(request, 'Password does not match')
                return redirect('register')  
    else:
        return render(request, 'register.html')



@login_required(login_url='loginadm')
def fileup(request, file_root):
    if request.method == "POST":
        form = fileupform(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            namesplit = os.path.splitext(file.name)
            filetype = namesplit[1].lower()
            rawsize = file.size
            par_folder = Folder.objects.get(pk=file_root)

            # Save the file
            filesv = File.objects.create(filename=namesplit[0], file_type=filetype, size=rawsize, folder_root=par_folder, file=file)
            filesv.save()
    
            # Generate preview if needed
            file_path = os.path.join(settings.MEDIA_ROOT, filesv.file.name)
            if filetype in ['.pdf']:
                images = pdf2image.convert_from_path(file_path, first_page=1, last_page=1)
                preview_path = os.path.join(settings.MEDIA_ROOT, 'previews', f'{filesv.id}.png')
                images[0].save(preview_path, 'PNG')
                filesv.img = f'previews/{filesv.id}.png'
            elif filetype in ['.png', '.jpg', '.jpeg', '.gif']:
                filesv.img = filesv.file.name
            else:
                filesv.img = None  # or set a default image for unsupported types

            filesv.save()
            return redirect(f"/manage/f/{file_root}")
    else:
        form = fileupform()

    return render(request, 'manage.html', {'form': form})



@login_required(login_url='loginadm')
def folderup(request, file_root):
    foldname = request.POST['foldname']
    
    par_folder = Folder.objects.get(pk=file_root)
    
    newfold = Folder.objects.create(folder_name = foldname, parent_folder = par_folder)
    newfold.save()
    return redirect("/manage/f/" + str(file_root))
        

      
def delete_file(request, pk):
    file_root = File.objects.get(pk = pk).folder_root.id
    file_obj = get_object_or_404(File, pk=pk)
    
    file_path = file_obj.file.path
    
    if file_obj.file:
        file_obj.file.delete(save=False)
        file_obj.img.delete()
    
    file_obj.delete()
    
    return redirect("/manage/f/" + str(file_root))


def logoutusr(request):
    logout(request)
    messages.success(request, ("You Were Logged Out!"))
    return redirect('/online/f/1')


    
@login_required(login_url='loginusr')
def download_file(request, pk):
    file_obj = get_object_or_404(File, pk=pk)
    
    file_path = file_obj.file.path
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=file_obj.file_type)
        response['Content-Disposition'] = f'attachment; filename={file_obj.filename+file_obj.file_type}'
        return response

  
    
@login_required(login_url='loginadm')
def move(request, type, pk):
    newfk = request.POST['newfk']
    newname = request.POST['newname']
    
    if type == "file":
        file = File.objects.get(pk = pk)

        file.folder_root_id = newfk
        file.save()
    elif type == "folder":
        folder = Folder.objects.get(pk = pk)
        
        folder.parent_folder_id = newfk
        folder.folder_name = newname
        folder.save()
        
    return redirect("/manage/f/" + str(newfk))



def delete_folder_contents(folder):
    for file_obj in File.objects.filter(folder_root=folder):
        file_obj.file.delete()
        file_obj.img.delete()
        file_obj.delete()

    for subfolder in Folder.objects.filter(parent_folder=folder):
        delete_folder_contents(subfolder)

    folder.delete()



def delete_folder_and_contents(request, pk):
    root = Folder.objects.get(pk = pk).parent_folder.id
    folder = get_object_or_404(Folder, pk = pk)
    delete_folder_contents(folder)
    return redirect('/manage/f/' + str(root))



def search_file(request):
    quest = request.GET.get('quest', '')
    resi = []
    reso = []
    
    resi = File.objects.filter(filename__contains = quest)
    reso = Folder.objects.filter(folder_name__contains = quest)
    
    cont = {
        "infolder" : reso,
        "infile" : resi
    }

    return render(request, 'manage.html', cont)   


def search_fileu(request):
    quest = request.GET.get('quest', '')
    resi = []
    reso = []
    
    resi = File.objects.filter(filename__contains = quest)
    reso = Folder.objects.filter(folder_name__contains = quest)
    
    cont = {
        "infolder" : reso,
        "infile" : resi
    }

    return render(request, 'online.html', cont)   


@login_required(login_url='loginusr')
def view_pdf(request, file_id):
    flsrc = get_object_or_404(File, pk=file_id)
    file_path = flsrc.file.path  # Correctly handle the file path
    
    try:
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404("File not found")