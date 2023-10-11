from framework import handlerDecorator, LoggerInstance


def rawHandler(event, _, logger: LoggerInstance):
    raise Exception("Not implemented")


handler = handlerDecorator(rawHandler)
