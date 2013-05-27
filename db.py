from app import mongo


class Flower(object):

    required = ['name', 'url', 'image_url', 'price']

    def __init__(self, *args, **kwargs):
        for arg in args:
            for key in arg:
                setattr(self, key, arg[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def validate(self):
        # Make sense all required fields are present.
        # Else raises an exception.
        for require in self.required:
            if not self.__dict__.get(require):
                raise Exception('"{}" is not present'.format(require))
        return True

    @property
    def data(self):
        # Validates the data and turns it into a dict.
        self.validate()
        return self.__dict__


def update_or_create(data):
    # Try to find the flower based on the url.
    flower = mongo.db.flower.find_one({"url": data['url']})
    # Already have the flower in the database.
    if flower:
        flower.update(data)
        mongo.db.flower.save(flower)
    else:
        flower = mongo.db.flower.insert(data)
    return flower
