from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.conf import settings
from django.shortcuts import redirect
from django.dispatch import receiver
import boto
import celery
import uuid
import json
from boto.s3.key import Key
from models import *


def get_s3_bucket():
	s3 = boto.connect_s3(settings.AWS_ACCESS_KEY, settings.AWS_ACCESS_SECRET)
	bucket = s3.lookup(settings.S3_BUCKET)
	return bucket

"""
	{
		"build_id": int,  
		"type": str
	}
"""
@csrf_exempt
def receive_upload(request):
	auth_header = request.META.get("HTTP_AUTHORIZATION", None)
	if auth_header is None:
		return HttpResponse('Unauthorized', status=401)

	key_pair = auth_header[7:].split(":")
	user = User.objects.get(username=key_pair[0])
	api_key = user.api_key
	if api_key.key != key_pair[1]:
		return HttpResponse('Invalid Key Pair', status=401)

	artifact_type = ArtifactType.objects.get(friendly_name=request.POST['type'])
	created_artifact = Artifact.objects.create(a_type=artifact_type, build_id=request.POST['build_id'], is_secure=True)
	return_data = {'id': created_artifact.pk, 'created': True}

	uploaded_files = request.FILES
	if uploaded_files is None:
		return HttpResponse("No files uploaded", status=400)

	payload = uploaded_files.get("payload", None)
	if payload is None:
		return HttpResponse("Payload not found", status=400)

	post_artifact_to_s3.delay(created_artifact.pk, payload.read())

	return HttpResponse(json.dumps(return_data), status=201)


@celery.task()
def post_artifact_to_s3(artifact_id, artifact_data):
	bucket = get_s3_bucket()
	artifact_uuid = str(uuid.uuid4())
	artifact_key = Key(bucket, artifact_uuid)
	artifact_key.set_contents_from_string(artifact_data)

	artifact = Artifact.objects.get(pk=artifact_id)
	artifact.is_secure = True
	artifact.secure_uuid = artifact_uuid
	artifact.save()


def artifact_download_redirect(a_id):
	art = Artifact.objects.get(pk=a_id)
	filename = "%s_%s%s" % (art.a_type.slug, art.build_id, art.a_type.extension)
	if art.is_secure:
		bucket = get_s3_bucket()
		if bucket is None:
			return
		key = bucket.lookup(art.secure_uuid)
		return redirect(key.generate_url(30, response_headers={'response-content-disposition': 'attachment; filename=%s' % (filename)}))
	else:
		response = HttpResponseRedirect(art.public_url)
		response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
		return response


@login_required
def download_artifact_by_id(request, a_id):
	return artifact_download_redirect(a_id)


@login_required
def build_artifact_download_redirect(request, build_id, a_type):
	build = Build.objects.get(pk=build_id)
	art = build.artifacts.get(a_type__slug=a_type)
	return artifact_download_redirect(art.pk)


@receiver(pre_delete, sender=Artifact)
def delete_s3_uploaded_artifact(sender, instance, **kwargs):
	if instance.is_secure:
		bucket = get_s3_bucket()
		if bucket is None:
			return
		key = bucket.lookup(instance.secure_uuid)
		if key:
			key.delete()

