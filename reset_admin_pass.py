#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Cambiar contraseña del admin
admin_user = User.objects.get(username='admin@admin.cl')
admin_user.set_password('admin123')
admin_user.save()
print(f"Contraseña del admin actualizada: {admin_user.username}")
