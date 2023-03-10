from dataclasses import dataclass
from azinvoicer.invoice_mappers import Environnement
import datetime
import pandas as pd


@dataclass
class InvoiceRecord:

    meterId: str
    serviceFamily: str
    meterCategory: str
    meterName: str
    resourceLocation: str
    billedCost: float
    tags: str
    partNumber: str
    resourceGroupLocation: str
    env: Environnement


@dataclass
class InvoiceStats:
    startDate: datetime
    endDate: datetime
    parsedLines: int
    parsedLinesWithoutEnv: int
    totalBilled: float
    totalBilledEnvs: float
    currency: str
    billedDays: int
    data: pd.DataFrame
