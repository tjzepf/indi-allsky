from .generic import GenericFileTransfer
#from .exceptions import AuthenticationFailure
from .exceptions import ConnectionFailure
#from .exceptions import TransferFailure

from pathlib import Path
#from datetime import datetime
#from datetime import timedelta
import socket
import time
#import urllib3.exceptions
from google.cloud import storage
from google.api_core.client_options import ClientOptions
import logging

logger = logging.getLogger('indi_allsky')


class gcp_storage(GenericFileTransfer):
    def __init__(self, *args, **kwargs):
        super(gcp_storage, self).__init__(*args, **kwargs)

        self._port = 443


    def connect(self, *args, **kwargs):
        super(gcp_storage, self).connect(*args, **kwargs)

        creds_file = kwargs['creds_file']
        #region = kwargs['region']
        #host = kwargs['hostname']  # endpoint_url
        #tls = kwargs['tls']
        #cert_bypass = kwargs['cert_bypass']


        #if cert_bypass:
        #    verify = False
        #else:
        #    verify = True


        options = ClientOptions(
            credentials_file=creds_file,
        )

        self.client = storage.Client(
            client_options=options,
        )


    def close(self):
        super(gcp_storage, self).close()


    def put(self, *args, **kwargs):
        super(gcp_storage, self).put(*args, **kwargs)

        local_file = kwargs['local_file']
        bucket = kwargs['bucket']
        key = kwargs['key']
        #storage_class = kwargs['storage_class']
        #acl = kwargs['acl']
        #metadata = kwargs['metadata']

        local_file_p = Path(local_file)


        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)


        #extra_args = dict()

        # cache 30 days
        #extra_args['CacheControl'] = 'max-age=2592000'


        if local_file_p.suffix in ['.jpg', '.jpeg']:
            content_type = 'image/jpeg'
        elif local_file_p.suffix in ['.mp4']:
            content_type = 'video/mp4'
        elif local_file_p.suffix in ['.png']:
            content_type = 'image/png'
        elif local_file_p.suffix in ['.webm']:
            content_type = 'video/webm'
        elif local_file_p.suffix in ['.webp']:
            content_type = 'image/webp'
        else:
            content_type = 'application/octet-stream'


        #if acl:
        #    extra_args['ACL'] = acl  # all assets are normally publicly readable


        #if storage_class:
        #    extra_args['StorageClass'] = storage_class


        generation_match_precondition = 0


        start = time.time()

        try:
            blob.upload_from_filename(
                str(local_file_p),
                if_generation_match=generation_match_precondition,
                timeout=self._timeout,
                content_type=content_type,
            )
        except socket.gaierror as e:
            raise ConnectionFailure(str(e)) from e
        except socket.timeout as e:
            raise ConnectionFailure(str(e)) from e
        except ConnectionRefusedError as e:
            raise ConnectionFailure(str(e)) from e
        #except urllib3.exceptions.ReadTimeoutError as e:
        #    raise ConnectionFailure(str(e)) from e

        upload_elapsed_s = time.time() - start
        local_file_size = local_file_p.stat().st_size
        logger.info('File transferred in %0.4f s (%0.2f kB/s)', upload_elapsed_s, local_file_size / upload_elapsed_s / 1024)


