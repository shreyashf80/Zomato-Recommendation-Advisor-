from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from datasets import Dataset, DatasetDict, load_dataset


@dataclass(frozen=True)
class LoadedDataset:
    dataset_id: str
    split: str
    dataset: Dataset


def load_hf_dataset(dataset_id: str, *, split_preference: tuple[str, ...] = ("train",)) -> LoadedDataset:
    """
    Loads the Hugging Face dataset and returns a single split as a Dataset.

    Note: we intentionally do not assume the dataset has a particular split name,
    but we prefer common names like "train" when present.
    """
    ds = load_dataset(dataset_id)

    if isinstance(ds, Dataset):
        return LoadedDataset(dataset_id=dataset_id, split="(single)", dataset=ds)

    if not isinstance(ds, DatasetDict):
        raise TypeError(f"Unexpected dataset type: {type(ds)}")

    for preferred in split_preference:
        if preferred in ds:
            return LoadedDataset(dataset_id=dataset_id, split=preferred, dataset=ds[preferred])

    # Fall back to first available split.
    first_split = next(iter(ds.keys()))
    return LoadedDataset(dataset_id=dataset_id, split=first_split, dataset=ds[first_split])


def maybe_set_hf_home(hf_home: Optional[str]) -> None:
    """
    Store Hugging Face / datasets caches under the project (writable in CI/sandbox).
    """
    if not hf_home:
        return

    cache_root = os.path.abspath(hf_home)
    os.makedirs(cache_root, exist_ok=True)

    hub_cache = os.path.join(cache_root, "hub")
    datasets_cache = os.path.join(cache_root, "datasets")
    os.makedirs(hub_cache, exist_ok=True)
    os.makedirs(datasets_cache, exist_ok=True)

    os.environ["HF_HOME"] = cache_root
    os.environ["HF_HUB_CACHE"] = hub_cache
    os.environ["HUGGINGFACE_HUB_CACHE"] = hub_cache
    os.environ["HF_DATASETS_CACHE"] = datasets_cache
    # Prevent fallback to user home cache dirs.
    os.environ["XDG_CACHE_HOME"] = cache_root

