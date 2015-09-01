from math import ceil
import math
import random
from safe_eval import safe_eval
from traceback import format_exc

def authorised_to_shup(source, owner):
    return True

last_request = "was nothing"
context = {}

def eval_answer(input, source):
    global context
    context.update({
        'answer_to_this_input': 0,
        'request_source': source,
        'random': random,
        'math': math,
    })
    safe_eval('answer_to_this_input = ' + input, context)
    return context['answer_to_this_input']

def what_to_say(bot, source, request, private):
    global last_request
    if request.startswith("eval: "):
        input = request[len('eval: '):]
        if last_request == input:
            last_request = "skip this one"
            return []
        else:
            last_request = input
        response = eval_say(bot, source, input, private)

        new_lines_response = []
        for line in response:
            new_lines_response.extend(line.split('\n'))

        safe_line_length_response = []
        for line in new_lines_response:
            if len(line) > 125:
                line_count = int(ceil(len(line) / 125.))
                for line_start in range(line_count):
                    safe_line_length_response.append(line[line_start * 125: (line_start + 1) * 125])
            else:
                safe_line_length_response.append(line)

        print safe_line_length_response
        print [len(thing) for thing in safe_line_length_response]
        if len(safe_line_length_response) > 20:
            return ["{}: that's too much to say; I can't be fucked".format(source)]
        return safe_line_length_response
    return []

def eval_say(bot, source, input, private):
    banned_phrases = ["exit()", "help()"]
    for banned_phrase in banned_phrases:
        if banned_phrase in input:
            answer = "go away"
            break
    else:
        try:
            answer = eval_answer(input, source)
        except Exception as e:
            print format_exc()
            print e
            answer = e

    return ["{}: {}".format(source, answer)]

