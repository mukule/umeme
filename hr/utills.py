# utils.py
from django.conf import settings


def check_admin_roles(user):
    is_authenticated = user.is_authenticated
    is_master = is_authenticated and user.is_superuser
    is_ict = is_authenticated and user.function == 10
    is_hradmin = is_authenticated and user.function == 1
    is_superuser = is_ict or is_master
    is_superadmin = is_hradmin or is_superuser
    is_post1 = is_authenticated and user.function == 2
    is_post2 = is_authenticated and user.function == 3
    is_pub1 = is_authenticated and user.function == 4
    is_pub2 = is_authenticated and user.function == 5
    is_edit1 = is_authenticated and user.function == 6
    is_edit2 = is_authenticated and user.function == 7
    is_del1 = is_authenticated and user.function == 8
    is_del2 = is_authenticated and user.function == 9

    is_hrpostjobs = is_superadmin or is_post1
    is_hrpostinterns = is_superadmin or is_post2
    is_hrpubjobs = is_superadmin or is_pub1
    is_hrpubinterns = is_superadmin or is_pub2
    is_hreditjobs = is_superadmin or is_edit1
    is_hreditinterns = is_superadmin or is_edit2
    is_hrdeljobs = is_superadmin or is_del1
    is_hrdelinterns = is_superadmin or is_del2

    return {
        'is_master': is_master,
        'is_superuser': is_superuser,
        'is_superadmin': is_superadmin,
        'is_hrpostjobs': is_hrpostjobs,
        'is_hrpostinterns': is_hrpostinterns,
        'is_hrpubjobs': is_hrpubjobs,
        'is_hrpubinterns': is_hrpubinterns,
        'is_hreditjobs': is_hreditjobs,
        'is_hreditinterns': is_hreditinterns,
        'is_hrdeljobs': is_hrdeljobs,
        'is_hrdelinterns': is_hrdelinterns
    }
