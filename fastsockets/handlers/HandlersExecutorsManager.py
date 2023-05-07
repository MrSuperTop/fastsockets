import asyncio
from collections import defaultdict
from typing import Generic, TypeVar

from fastsockets.handlers.Executor import HandlersExecutor
from fastsockets.types.BaseMessage import BaseMessage

ExecutorGroupIdentifier = TypeVar('ExecutorGroupIdentifier')
SingleExecutorIdentifier = int
ExecutorsStore = defaultdict[
    ExecutorGroupIdentifier,
    dict[SingleExecutorIdentifier, HandlersExecutor]
]

class HandlersExecutorsManager(
    Generic[ExecutorGroupIdentifier]
):
    def __init__(self) -> None:
        self._executors_store: ExecutorsStore = defaultdict(lambda: dict())

    def add_executor(
        self,
        group_identifier: ExecutorGroupIdentifier,
        executor: HandlersExecutor
    ) -> SingleExecutorIdentifier:
        executor_id = id(executor)
        self._executors_store[group_identifier][executor_id] = executor

        return executor_id

    def remove_executor(
        self,
        group_identifier: ExecutorGroupIdentifier,
        unique_indentifier: SingleExecutorIdentifier
    ) -> bool:
        if group_identifier not in self._executors_store:
            return False

        current_indentifier_executors = self._executors_store[group_identifier]
        if unique_indentifier not in current_indentifier_executors:
            return False

        del current_indentifier_executors[unique_indentifier]
        return True

    # * This method of broadcasting messages is pretty alright for isnstances, where
    # * the clients do not have much latency
    # * Maybe, doing it this way has some advantages, we will have to see
    # * https://websockets.readthedocs.io/en/stable/topics/broadcast.html#per-client-queues
    # * Refer to the information in fastsockets/__init__.py to read more about this

    async def broadcast(
        self,
        group_identifier: ExecutorGroupIdentifier,
        message: BaseMessage
    ):
        executors = self._executors_store[group_identifier].values()

        for executor in executors:
            asyncio.create_task(executor.send_message(message))
