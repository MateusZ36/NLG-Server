import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Text

from rasa.core.nlg.response import TemplatedNaturalLanguageGenerator
from rasa.shared.constants import RESPONSE_CONDITION
from rasa.shared.core.domain import Domain
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.utils.endpoints import EndpointConfig

logger = logging.getLogger(__name__)


class CustomNLG(TemplatedNaturalLanguageGenerator):

    def __init__(self, endpoint_config: EndpointConfig, domain: Domain) -> None:
        super().__init__(domain.responses)
        self.endpoint_config = endpoint_config

    async def generate(
        self,
        utter_action: Text,
        tracker: DialogueStateTracker,
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[Dict[Text, Any]]:
        filled_slots = tracker.current_slot_values()
        generated = self.generate_from_slots(utter_action, filled_slots, output_channel, **kwargs)

        return {**generated, **tracker.latest_message.metadata}

    def _matches_filled_slots(
        self, filled_slots: Dict[Text, Any], response: Dict[Text, Any],
    ) -> bool:
        constraints = response.get(RESPONSE_CONDITION)
        for constraint in constraints:
            constraint_name = constraint["name"]
            constraint_value = constraint["value"]
            slot_value = filled_slots.get(constraint_name)
            if constraint_value in ["set", "null"]:
                if constraint_value == "set" and slot_value is None:
                    return False
                elif constraint_value == "null" and slot_value is not None:
                    return False
            elif slot_value != constraint_value:
                return False

        return True
