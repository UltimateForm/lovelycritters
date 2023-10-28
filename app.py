#!/usr/bin/env python3
import os

import aws_cdk as cdk

from client.aws.clientStack import LC_ClientStack
from internal.aws.internalStack import LC_InternalStack

app = cdk.App()
internalStack = LC_InternalStack(app, "LovelyCritters-InternalStack")
LC_ClientStack(app, "LovelyCritters-ClientStack").add_dependency(internalStack)
app.synth()
