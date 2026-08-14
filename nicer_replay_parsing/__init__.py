import sys

from . import imp

sys.modules["imp"] = imp
import heroprotocol
from .parse_replay import parse_replay, print_replay_contents
from .model import *
