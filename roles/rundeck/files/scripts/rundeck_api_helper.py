#!/usr/bin/python

import requests
import click
from urlparse import urljoin
import ConfigParser
import xmltodict
import json


class RundeckApiHelper:
    headers = {}

    def __init__(self, config_file):
        self.config = self.__read_config(config_file)
        self.__create_user_session()
        self.log = self.__init_logger()

    @staticmethod
    def __read_config(config_file):
        """
        Read and parse configuration file

        :param config_file: PATH to config file
        :return: instance of ConfigParser
        """
        config = ConfigParser.ConfigParser()
        config.read(config_file)

        return config

    def __init_logger(self):
        """
        Initiates logger instance and logger stream

        :return: True
        """
        if not self.is_debugger_on():
            return True

        import logging
        import logging.handlers

        log = logging.getLogger()
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(format=fmt)
        formatter = logging.Formatter(fmt)
        handler = logging.handlers.RotatingFileHandler("helper.log", mode='a')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

        return log

    def is_debugger_on(self):
        """
        Config method for checking state of debugger settings
        :return: True when debugging is ON, otherwise False
        """
        if self.config.get('debug', 'level') < 1:
            return False

        return True

    def logit(self, msg='none'):
        """
        Method logs messages to predefined logger stream

        :param msg: Message content
        :return: True
        """
        if not self.is_debugger_on():
            return True

        self.log.warn(msg)

        return True

    def __create_user_session(self):
        self.headers["X-Rundeck-Auth-Token"] = self.config.get('api', 'token')

    def import_job_from_yaml(self, project_id, yaml_file_path):
        """
        Send import jobs API call:
        http://rundeck.org/docs/api/index.html#importing-jobs

        :param project_id: id of the project
        :param yaml_file_path: Absolute path to json file
        :return: yaml with freshly imported job data
        """

        _url = 'project/%s/jobs/import' % project_id

        req = self.send_post_request(
            _url,
            'application/yaml',
            open(yaml_file_path, "r").read())

        # yup, we're sending YAML request and get back XML
        # and now we have to decide whether job was created or not and return
        # simple answer

        xml_object = xmltodict.parse(req.text)
        json_response = json.loads(json.dumps(xml_object))

        ret = 'Error during importing job %s' % yaml_file_path

        if req.status_code != 200:
            return "%s (HTTP error code: %s" % (ret, req.status_code)

        if json_response['result']['@success'] == 'true':
            if int(json_response['result']['failed']['@count']) > 0:
                if 'Job already exists with this UUID' in json_response['result']['failed']['job']['error']:
                    ret = 'Job already exists with this UUID'
            elif int(json_response['result']['succeeded']['@count']) > 0:
                ret = 'Job has been created successfully'

        return ret

    def import_project_from_json(self, json_file_path):
        """
        Send import project API call:
        http://rundeck.org/docs/api/index.html#project-creation

        :param json_file_path: Absolute path to json file
        :return: String with status code
        """

        _url = 'projects'

        req = self.send_post_request(
                                    _url,
                                    'application/json',
                                    open(json_file_path, "r").read())

        if req.status_code == 201:
            msg = 'Project was created (HTTP response code: %s)' % req.status_code
        elif req.status_code == 409:
            msg = 'Project already exists (HTTP response code: %s)' % req.status_code
        else:
            msg = 'Unknown behaviour, check log file for details (HTTP response code: %s)' % req.status_code

        return msg

    def send_post_request(self, url, content_type, payload):
        """
        Send post API request

        :param url: URL PATH w/out API version
        :param content_type: content type (e.g. application/xml)
        :param payload: Payload to send
        :return: request object
        """

        url = urljoin(self.config.get('api', 'url'), url)
        _headers = {
            'content-type': content_type
        }

        req = requests.post(
                            url,
                            headers=dict(self.headers.items() + _headers.items()),
                            data=payload)

        self.logit(req.text)

        return req

    # http://rundeck.org/docs/api/index.html#getting-project-info
    def get_project_info(self, project_id):
        _url = ('project/%s' % project_id)
        headers = {
            'Accept': 'application/json'
        }
        req = self.send_get_request(_url, _headers=headers)

        return req.text

    def export_jobs(self, project_id, _format=None):
        """
        Exporting jobs
        http://rundeck.org/docs/api/index.html#exporting-jobs

        :param project_id: id of the project
        :param _format: xml / yaml, default yaml
        :return:
        """

        if _format is None:
            _format = 'yaml'

        params = {
            'format': _format
        }

        _url = ('project/%s/jobs/export' % project_id)
        req = self.send_get_request(_url, _params=params)

        return req.text

    # http://rundeck.org/docs/api/index.html#project-configuration
    def get_project_configuration(self, project_id):
        _url = ('project/%s/config' % project_id)
        req = self.send_get_request(_url)

        return req.text

    def send_get_request(self, url, _headers=None, _params=None):

        if _headers is None:
            _headers = {}

        if _params is None:
            _params = {}

        print(dict(self.headers.items() + _headers.items()))
        url = urljoin(self.config.get('api', 'url'), url)

        req = requests.get(
                url,
                headers=dict(self.headers.items() + _headers.items()),
                params=_params
        )

        self.logit(req.text)

        return req


@click.group()
@click.argument('config_file')
@click.pass_context
def cli(ctx, config_file):
    ctx.obj = RundeckApiHelper(config_file)


@cli.command()
@click.argument('project_id')
@click.pass_obj
def get_project_info(ctx, project_id):
    """
    Click child command invoking get_project_info ctx method

    :param ctx: context object
    :param project_id: rundeck project name
    :return: json with project data (or with error information)
    """
    print(ctx.get_project_info(project_id))


@cli.command()
@click.argument('json_file', type=click.Path(exists=True))
@click.pass_obj
def create_project(ctx, json_file):
    """
    Click child command invoking create_project ctx method

    :param ctx: context object
    :param json_file: Absolute path to json file with project metadata
    :return: json with freshly created project data
    """
    print(ctx.import_project_from_json(json_file))


@cli.command()
@click.argument('project_id')
@click.argument('yaml_file', type=click.Path(exists=True))
@click.pass_obj
def create_job(ctx, project_id, yaml_file):
    """
    Click child command invoking create_project ctx method

    :param ctx: context object
    :param project_id: rundeck project name
    :param yaml_file: Absolute path to yaml file with job metadata
    :return: json with freshly created job data
    """
    print(ctx.import_job_from_yaml(project_id, yaml_file))

if __name__ == '__main__':
    cli()
