import sys

from . import imp

sys.modules["imp"] = imp
import heroprotocol
from .parse_replay import parse_replay
from .model import *
