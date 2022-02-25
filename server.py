import argparse
import os

from decouple import config
from sanic import Sanic, response
from rasa.constants import ENV_SANIC_BACKLOG, DEFAULT_SANIC_WORKERS
import logging
from rasa.shared.core.domain import Domain
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.utils.endpoints import EndpointConfig

from generator import CustomNLG

logger = logging.getLogger(__name__)


DEFAULT_SERVER_PORT = 5065


class NlgServer:

    def __init__(self, domain_path, port, workers):
        self.domain_path = domain_path
        self.domain = self.load_domain()
        self.port = port
        self.workers = workers

    def load_domain(self):
        return Domain.load(self.domain_path)

    async def generate_response(self, nlg_call):
        kwargs = nlg_call.get("arguments", {})
        response = nlg_call.get("response")
        sender_id = nlg_call.get("tracker", {}).get("sender_id")
        events = nlg_call.get("tracker", {}).get("events")
        tracker = DialogueStateTracker.from_dict(sender_id, events, self.domain.slots)
        channel_name = nlg_call.get("channel").get("name")

        return await CustomNLG(EndpointConfig(), self.domain).generate(
            response, tracker, channel_name, **kwargs
        )

    def run_server(self):
        app = Sanic(__name__)

        @app.route("/nlg", methods=["POST"])
        async def nlg(request):
            """Endpoint which processes the Core request for a bot response."""
            nlg_call = request.json
            bot_response = await self.generate_response(nlg_call)

            return response.json(bot_response)
        if config("RASA_ENVIRONMENT", default="DEV") == "DEV":
            @app.route("/reload", methods=["GET"])
            async def reload(request):
                self.domain = self.load_domain()
                response_dict = {
                    "text": f"Loaded {len(self.domain.responses)} responses",
                    "domain_path": self.domain_path
                }

                show_responses_arg = request.args.get("show_responses")
                if show_responses_arg == "title":
                    response_dict["responses"] = list(self.domain.responses.keys())
                elif show_responses_arg == "full":
                    response_dict["responses"] = self.domain.responses
                return response.json(
                    response_dict
                )

        app.run(
            host="0.0.0.0",
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

    return parser


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    arg_parser = create_argument_parser()
    cmdline_args = arg_parser.parse_args()

    NlgServer(cmdline_args.domain, cmdline_args.port, cmdline_args.workers).run_server()
