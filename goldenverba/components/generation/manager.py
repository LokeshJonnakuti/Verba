import tiktoken
from wasabi import msg
from typing import Optional, Iterator

from goldenverba.components.generation.interface import Generator
from goldenverba.components.generation.GPT4Generator import GPT4Generator
from goldenverba.components.generation.GPT3Generator import GPT3Generator
from goldenverba.components.generation.Llama2Generator import Llama2Generator
from goldenverba.components.generation.CohereGenerator import CohereGenerator


class GeneratorManager:
    def __init__(self):
        self.generators: dict[str, Generator] = {
            "GPT4Generator": GPT4Generator(),
            "GPT3Generator": GPT3Generator(),
            "CohereGenerator": CohereGenerator(),
            "Llama2Generator": Llama2Generator(),
        }
        self.selected_generator: Generator = self.generators["GPT3Generator"]

    async def generate(
        self,
        queries: list[str],
        context: list[str],
        conversation: Optional[dict] = None,
    ) -> str:
        """Generate an answer based on a list of queries and list of contexts, and includes conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns str - Answer generated by the Generator
        """
        conversation = {} if conversation is None else conversation
        return await self.selected_generator.generate(
            queries,
            context,
            self.truncate_conversation_items(
                conversation, int(self.selected_generator.context_window * 0.375)
            ),
        )

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: Optional[dict] = None,
    ) -> Iterator[dict]:
        """Generate a stream of response dicts based on a list of queries and list of contexts, and includes conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns Iterator[dict] - Token response generated by the Generator in this format {system:TOKEN, finish_reason:stop or empty}
        """
        conversation = {} if conversation is None else conversation
        async for result in self.selected_generator.generate_stream(
            queries,
            context,
            self.truncate_conversation_items(
                conversation, int(self.selected_generator.context_window * 0.375)
            ),
        ):
            yield result

    def truncate_conversation_dicts(
        self, conversation_dicts: list[dict[str, any]], max_tokens: int
    ) -> list[dict[str, any]]:
        """
        Truncate a list of conversation dictionaries to fit within a specified maximum token limit.

        @parameter conversation_dicts: List[Dict[str, any]] - A list of conversation dictionaries that may contain various keys, where 'content' key is present and contains text data.
        @parameter max_tokens: int - The maximum number of tokens that the combined content of the truncated conversation dictionaries should not exceed.

        @returns List[Dict[str, any]]: A list of conversation dictionaries that have been truncated so that their combined content respects the max_tokens limit. The list is returned in the original order of conversation with the most recent conversation being truncated last if necessary.

        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        accumulated_tokens = 0
        truncated_conversation_dicts = []

        # Start with the newest conversations
        for item_dict in reversed(conversation_dicts):
            item_tokens = encoding.encode(item_dict["content"], disallowed_special=())

            # If adding the entire new item exceeds the max tokens
            if accumulated_tokens + len(item_tokens) > max_tokens:
                # Calculate how many tokens we can add from this item
                remaining_space = max_tokens - accumulated_tokens
                truncated_content = encoding.decode(item_tokens[:remaining_space])

                # Create a new truncated item dictionary
                truncated_item_dict = {
                    "type": item_dict["type"],
                    "content": truncated_content,
                    "typewriter": item_dict["typewriter"],
                }

                truncated_conversation_dicts.append(truncated_item_dict)
                break

            truncated_conversation_dicts.append(item_dict)
            accumulated_tokens += len(item_tokens)

        # The list has been built in reverse order so we reverse it again
        return list(reversed(truncated_conversation_dicts))

    def set_generator(self, generator: str) -> bool:
        if generator in self.generators:
            self.selected_generator = self.generators[generator]
            return True
        else:
            msg.warn(f"Generator {generator} not found")
            return False

    def get_generators(self) -> dict[str, Generator]:
        return self.generators
