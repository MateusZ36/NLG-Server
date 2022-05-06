import argparse
import os

from decouple import config
from rasa.core.nlg import TemplatedNaturalLanguageGenerator, NaturalLanguageGenerator
from rasa.utils.endpoints import EndpointConfig
from sanic import Sanic, response
from rasa.constants import ENV_SANIC_BACKLOG, DEFAULT_SANIC_WORKERS
import logging
from rasa.shared.core.domain import Domain
from rasa.shared.core.trackers import DialogueStateTracker


logger = logging.getLogger(__name__)


DEFAULT_SERVER_PORT = 5065


class NlgServer:
    def __init__(self, domain_path, port, workers, nlg_class=TemplatedNaturalLanguageGenerator):
        self.domain = Domain.load(domain_path)
        if isinstance(nlg_class, str):
            self.nlg_class = NaturalLanguageGenerator.create(EndpointConfig(type=nlg_class), self.domain)
        else:
            self.nlg_class = nlg_class(self.domain.responses)
        self.domain_path = domain_path
        self.load_domain()
        self.port = port
        self.workers = workers

    def load_domain(self, debug_mode=None):
        self.domain = Domain.load(self.domain_path)
        self.nlg_class.responses = self.domain.responses
        debug_dict = {
            "text": f"Loaded {len(self.nlg_class.responses)} responses",
            "domain_path": self.domain_path
        }
        if debug_mode == "title":
            debug_dict["responses"] = list(self.domain.responses.keys())
        elif debug_mode == "full":
            debug_dict["responses"] = self.domain.responses

        return debug_dict

    async def generate_response(self, nlg_call):
        kwargs = nlg_call.get("arguments", {})
        response_arg = nlg_call.get("response")
        sender_id = nlg_call.get("tracker", {}).get("sender_id")
        events = nlg_call.get("tracker", {}).get("events")
        tracker = DialogueStateTracker.from_dict(sender_id, events, self.domain.slots)
        channel_name = nlg_call.get("channel").get("name")

        return await self.nlg_class.generate(response_arg, tracker, channel_name, **kwargs)

    def run_server(self):
        app = Sanic(__name__)

        @app.route("/nlg", methods=["POST"])
        async def nlg(request):
            nlg_call = request.json
            bot_response = await self.generate_response(nlg_call)
            return response.json(bot_response)

        if config("RASA_ENVIRONMENT", default="DEV") == "DEV":
            @app.route("/reload", methods=["GET"])
            async def reload(request):
                debug_response = self.load_domain(request.args.get("show_responses"))

                return response.json(
                    debug_response
                )

        app.run(
            host="localhost",
            port=self.port,
            workers=self.workers,
            backlog=int(os.environ.get(ENV_SANIC_BACKLOG, "100")),
        )


def create_argument_parser():
    parser = argparse.ArgumentParser(description="starts the nlg endpoint")
    parser.add_argument(
        "-p",
        "--port",
        default=DEFAULT_SERVER_PORT,
        type=int,
        help="port to run the server at",
    )
    parser.add_argument(
        "-w",
        "--workers",
        default=DEFAULT_SANIC_WORKERS,
        type=int,
        help="Number of processes to spin up",
    )
    parser.add_argument(
        "-d",
        "--domain",
        type=str,
        default=".",
        help="path of the domain file to load utterances from",
    )
    parser.add_argument(
        "--nlg",
        type=str,
        default=TemplatedNaturalLanguageGenerator,
        help="custom nlg class path",
    )

    return parser


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    arg_parser = create_argument_parser()
    cmdline_args = arg_parser.parse_args()

    NlgServer(
        cmdline_args.domain,
        cmdline_args.port,
        cmdline_args.workers,
        cmdline_args.nlg,
    ).run_server()
