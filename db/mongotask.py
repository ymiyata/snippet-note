from tornado import gen

class MongoTask(gen.Task):
    def get_result(self):
        result = super(MongoTask, self).get_result()
        if isinstance(result, gen.Arguments):
            args, kwargs = result
        else:
            args, kwargs = (result,), {}
        if kwargs.get('error'):
            raise kwargs['error']
        result, = args
        return result
