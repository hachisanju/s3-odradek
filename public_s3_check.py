# -*- coding: UTF-8
import os
import sys
import boto3
import signal

def signal_handler(sig, frame):
    print('\nExiting...')
    sys.exit(0)

def user_input_section(list_response):
    value = input('> ')
    os.system('cls' if os.name == 'nt' else 'clear')

    if value == 'list' and list_response!= '':
        for obj in list_response.get('Contents'):
            if obj.get('Key')[-1] == '/':
                continue
            else:
                print (obj.get('Key'))
        return False

    elif value == 'list':
        print('No values in list')
        return False
        
    else:
        return True

def get_bucket_policy(s3_client, bucket):
    print('Analyzing public status of bucket: {}'.format(bucket))
    try:
        get_response = s3_client.get_bucket_policy(Bucket=bucket)
        print('✗ [Get Bucket Policy] allowed')
    except Exception as e:
        if 'AccessDenied' in str(e):
            print('✓ [Get Bucket Policy] not allowed')
        else:
            print(e)

def main():
    session = boto3.Session(profile_name='seekertest2', region_name='us-east-1')
    s3_client = session.client('s3')

    with open('bucket_list.txt') as f:
        buckets_list = f.readlines()

    for bucket in buckets_list:
        get_response = ''
        list_response = ''
        bucket = bucket.replace('\n','')
        get_bucket_policy(s3_client, bucket)
        #LIST OBJECTS
        try:
            list_response = s3_client.list_objects_v2(Bucket=bucket)
            print('✗ [List Objects] allowed')
        except Exception as e:
            if 'AccessDenied' in str(e):
                print('✓ [List Objects] not allowed')
            else:
                print(e)
        #GET OBJECTS
        try:
            if list_response != '':
                for obj in list_response.get('Contents'):
                    if obj.get('Key')[-1] == '/':
                        continue
                    else:
                        try:
                            get_response = s3_client.get_object(Bucket=bucket,Key=obj.get('Key'))
                            print('✗ [Get Objects] allowed')
                        except Exception as e:
                            print('✓ [Get Objects] not allowed')
                        break
        except Exception as e:
            print('? There are probably no objects in this bucket.')
        #PUT OBJECTS
        try:
            put_response = s3_client.upload_file(Bucket=bucket, Filename='SECURITY_ALERT.txt', Key='SECURITY_ALERT.txt')
            print('✗ [Put Objects] allowed')
            try:
                delete_response = s3_client.delete_object(Bucket=bucket, Key='SECURITY_ALERT.txt')
                print('✗ [Delete Objects] allowed')
                put_response = s3_client.upload_file(Bucket=bucket, Filename='SECURITY_ALERT.txt', Key='SECURITY_ALERT.txt')
                try:
                    get_response = s3_client.get_object(Bucket=bucket,Key='SECURITY_ALERT.txt')
                    print('s3.amazonaws.com/{}/{}'.format(bucket,'SECURITY_ALERT.txt'))
                except Exception as e:
                    if 'AccessDenied' in str(e):
                        print('✓ [Get Objects] not allowed')
                    else:
                        print(e)
            except Exception as e:
                if 'AccessDenied' in str(e):
                    print('✓ [Delete Objects] not allowed')
                else:
                    print(e)
        except Exception as e:
            if 'AccessDenied' in str(e):
                print('✓ [Put Objects] not allowed')
            else:
                print(e)
        user_input = False
        while not (user_input):
            user_input = user_input_section(list_response)

    print('Finished. Exiting...')

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
