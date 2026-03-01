import asyncio
from agentmake import agentmake, DEFAULT_AI_BACKEND, unpack_instruction_content, unpack_system_content
from agentmake.utils.text_wrapper import get_stream_event_text
from agentmake.utils.read_assistant_response import is_openai_style
from biblemateweb import DEFAULT_MESSAGES

async def stream_output(messages, user_request, cancel_event=None, system=None, **kwargs):
    def get_next_chunk(iterator):
        """
        Runs in a separate thread. 
        Returns the next item, or None if the iterator is exhausted.
        """
        try:
            return next(iterator)
        except StopIteration:
            return None
        except Exception as e:
            return e  # Return the error to be handled in the main loop

    if "instruction" in kwargs:
        instruction_content = kwargs.pop("instruction")
        instruction_content = unpack_instruction_content(instruction_content)
        # refine user request
        user_request = instruction_content + "\n" + user_request

    if system == "auto":
        system = await stream_output(DEFAULT_MESSAGES, user_request, cancel_event, system="bible/create_agent", **kwargs)
        if not system or system.strip() == "[NO_CONTENT]":
            return None
        else:
            # refine response
            system = system.replace("should:", "should:\n")
            system = system.replace("examples:", "examples:\n")
            if system.startswith("```agent\n"):
                system = system[9:]
            if system.endswith("```"):
                system = system[:-3].strip()
    elif system is not None:
        system_content = unpack_system_content(system)
        system = None
        # refine user request
        user_request = f"""---

START OF YOUR NEW ROLE

---

{system_content}

---

START OF MY REQUEST

---

{user_request}"""

    # Print loading text
    print("Loading...", end="\r", flush=True)
    await asyncio.sleep(0)

    backend=kwargs.pop("backend", DEFAULT_AI_BACKEND)
    model=kwargs.pop("model", None)
    api_key=kwargs.pop("api_key", None)
    api_endpoint=kwargs.pop("api_endpoint", None)
    max_tokens=kwargs.pop("max_tokens", None)
    context_window=kwargs.pop("context_window", None)
    temperature=kwargs.pop("temperature", None)

    # run completion
    text_chunks = ""
    completion = await asyncio.to_thread(
        agentmake, 
        messages, 
        system=system,
        backend=backend, 
        model=model, 
        api_key=api_key,
        api_endpoint=api_endpoint,
        max_tokens=max_tokens,
        context_window=context_window,
        temperature=temperature,
        follow_up_prompt=user_request, 
        stream=True, 
        print_on_terminal=False, 
        stream_events_only=True, 
        **kwargs,
    )

    print("Running...  ", end="\r", flush=True)

    try:
        while cancel_event is None or not cancel_event.is_set():
            event = await asyncio.to_thread(get_next_chunk, completion)

            if event is None:
                break
            elif isinstance(event, Exception):
                print(f"\nStream interrupted: {str(event)}")
                break

            actual_backend = backend if backend else DEFAULT_AI_BACKEND
            if text_chunk := get_stream_event_text(event, openai_style=is_openai_style(actual_backend)):
                text_chunks += text_chunk
                print(text_chunk, end="", flush=True)
                await asyncio.sleep(0)

        if cancel_event is not None and cancel_event.is_set():
            print("\n[Cancelled!]")
        else:
            print() # Print newline when done

    except Exception as e:
        print(f"\n[Error: {str(e)}]")
        if cancel_event is not None:
            cancel_event.set()

    if cancel_event is not None and cancel_event.is_set():
        cancel_event = None
        return None
    
    return text_chunks.replace(" ", " ").replace("‑", "-")
