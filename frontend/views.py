from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from emubaby.settings import ORG_NAME
from datastore.models import *
from datastore.utils import get_build_query_set


@login_required
def index(request):
	num_builds = Build.objects.count()
	num_accessible_builds = Build.objects.count()
	return TemplateResponse(request, 'index.html', {'org_name': ORG_NAME, 'num_builds': num_builds, 'accessible_builds': num_accessible_builds})


@login_required
def latest(request):
	latest_build = Build.objects.latest('created')
	try:
		latest_starred = Build.objects.filter(starred=True).latest('created')
	except Exception as e:
		latest_starred = None
	return TemplateResponse(request, 'latest.html', {'latest_build': latest_build, 'latest_starred': latest_starred})


@login_required
def build_page(request, build_id):
	build = Build.objects.get(id=build_id)

	installers = Artifact.objects.filter(	a_type__installer_type__in=[ArtifactType.INSTALLER_TYPE_NORMAL,
																	ArtifactType.INSTALLER_TYPE_IPHONE,
																	ArtifactType.INSTALLER_TYPE_ANDROID],
											build__id=build_id)

	artifacts = Artifact.objects.filter(	a_type__installer_type=ArtifactType.INSTALLER_TYPE_NONE,
											build__id=build_id)

	extra_data_set = ExtraDataValue.objects.filter(build_id=build_id)
	return TemplateResponse(request, 'build.html', {'build': build, 'installers': installers, 'artifacts': artifacts, 'metadata_set': build.metadata.all(), 'extra_data_set': extra_data_set})


@login_required
def build_list_page(request):
	params = request.GET
	builds = get_build_query_set(params, Build.objects.all())
	if builds is None:
		builds = Build.objects.all()
	return TemplateResponse(request, 'build_list.html', {'builds': builds, 'metadata_set': params})


@login_required
def build_filter_page(request):
	all_metadata_categories = MetaDataCategory.objects.all()
	return TemplateResponse(request, 'filter_page.html', {'categories': all_metadata_categories})


@login_required
def profile_page(request):
	return TemplateResponse(request, 'profile_page.html', {'user': request.user})

