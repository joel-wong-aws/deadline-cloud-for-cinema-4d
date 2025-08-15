# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
from enum import Enum


class ErrorChecking(Enum):
    DEACTIVATE = "0"
    ACTIVATE = "1"


class FreezeDetection(Enum):
    DEACTIVATE = "0"
    ACTIVATE = "1"
