rm remote_date.sqlite3
appcfg.py download_data -e pawel.palucki@gmail.com --application=s~sh-cms --url=http://sh-cms.appspot.com/_ah/remote_api --filename=remote.sqlite3 --log_file=bin\copy_data.log --db_filename=skip --result_db_filename=skip
appcfg.py upload_data -e pawel.palucki@gmail.com --url=http://127.0.0.1:8080/remote_api --application=sh-cms --filename=remote.sqlite3 app --log_file=bin\copy_data.log --db_filename=skip

REM create config ale nie dziala
REM appcfg.py create_bulkloader_config --filename=loader.yaml --url=http://sh-cms.appspot.com/_ah/remote_api --application=s~sh-cms app