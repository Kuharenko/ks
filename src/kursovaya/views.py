from django.shortcuts import render,redirect
from forms import *
import os.path, time, re, errors_list
from subprocess import call, Popen
from threading import Timer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import auth
import shutil


@login_required
def compile(request):
    form = myForm(request.POST or None)
    if request.POST:
        usr = ""+request.user.username
        static_dir = "static/users/" + usr

        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

        source_code = 'source.cpp'
        output_file = static_dir + '/' + source_code.split('.')[0] + '.out'

        if os.path.exists(output_file):
            os.remove(output_file)

        src = open(static_dir + "/%s" % source_code, "w")
        src.write(request.POST.get('text').encode('utf-8'))
        src.close()

        input_file = open(static_dir + '/input.txt', "w")
        input_file.write("1234")
        input_file.close()

        src = open(static_dir + "/%s" % source_code, "r")

        a = str(src.read())

        deny = ['pwd', 'cd', 'apt', 'install', 'dir', 'sudo', 'mkdir', 'touch', 'nano']
        have_problem = False
        for cmd in deny:
            if re.search('(system)(\s)*[(](\s)*(\'|\")*(\s)*('+'%s'%cmd+')*(\s)*(\'|\")*(\s)*[)]*', a):
                have_problem = True
                fe = open(static_dir + '/logs.log', 'a')
                fe.write('System commands not use! :)')
                break

        src.close()

        errors_log = open(static_dir + "/logs.log", "w")
        call(["g++", static_dir + "/%s" % source_code, "-o", "%s" % output_file],
             stderr=errors_log,
             shell=False,
             )

        errors_log.close()
        print output_file

        while not os.path.exists(output_file):

            if os.stat(static_dir + '/logs.log').st_size == 0:
                time.sleep(1)
            else:
                print "Have problems"
                have_problem = True
                break

        if os.path.isfile(output_file) and not have_problem:
            cmd = ["./%s" % output_file]
            log = open(static_dir + "/output.log", 'w')
            kill = lambda process: process.kill()
            data = Popen(cmd, stdout=log, stderr=log, shell=True)
            my_timer = Timer(3, kill, [data])

            try:
                my_timer.start()
                stdout, stderr = data.communicate()
            finally:
                my_timer.cancel()

            log.flush()
            log.close()

            output_log = open(static_dir + "/output.log", "r")
            output = output_log.read()
            output_log.close()
            return render(request, 'index.html', {'form': form,
                                                  'data': data.returncode,
                                                  'output': output.replace('<<', '<< ').replace('\n', '<br>')})
        else:
            fe = open(static_dir + '/logs.log')
            data = fe.read()
            links = []
            for key, value in errors_list.list().iteritems():
                if re.search(key, data):
                    links.append(value)

            fe.close()
            return render(request, 'index.html', {'form': form,
                                                  'data': data.replace('<<', '<< ').replace('\n', '<br>'),
                                                  'link': set(links)})
    return render(request, 'index.html', {'form': form})


def register(request):
    registration_form = RegisterForm(request.POST or None)
    if request.POST:
        if registration_form.is_valid():
            usr = registration_form.save(commit=False)
            usr.password = make_password(request.POST.get('password'))
            usr.save()
            return redirect('login')
    return render(request, 'register.html',{'registration_form': registration_form})


def log_in(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('compile')
    return render(request,'log_in.html')


@login_required
def logout_page(request):
    usr = "" + request.user.username
    static_dir = "static/users/" + usr

    if os.path.exists(static_dir):
        shutil.rmtree('static/users/'+request.user.username)
    auth.logout(request)
    return redirect('login')