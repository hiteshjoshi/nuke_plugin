# Nuke plugin

## Just a plugin for nuke to send images to an image classfication server running on fastai and powered by Simple HTTP server Python.

To run,  Just do :

```shell
python3 http_server.py 'path_to_dir_containing_export.pkl'
```



To send image and get its prediction do this : 

```shell
curl -F "file=@/Users/hitesh/Projects/fastai/test.jpg" localhost:8000
```

