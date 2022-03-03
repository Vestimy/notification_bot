from jinja2 import Environment, DictLoader
from jinja2 import BaseLoader, Environment, TemplateNotFound
from os.path import exists, getmtime, join
from os import path

PATH = path.abspath(path.dirname(__file__))


class FoopkgLoader(BaseLoader):
    def __init__(self, path=PATH + "/templates"):
        self.path = path

    def get_source(self, environment, template):
        path = join(self.path, template)

        if not exists(path):
            raise TemplateNotFound(template)
        mtime = getmtime(path)
        with open(path) as f:
            source = f.read()
        return source, path, lambda: mtime == getmtime(path)


def my_func(url, **kwargs):
    env = Environment(loader=FoopkgLoader())
    template = env.get_template(url)

    return template.render(**kwargs)





