import uuid

def scramble(instance,filename):
    extension=filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(),extension)
