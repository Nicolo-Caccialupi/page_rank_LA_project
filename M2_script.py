# # Preprocessing Data
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import numpy as np
from scipy import sparse
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import islice

def build_transition():
    """Build S, the dangling-node mask and v in memory from the Wikipedia CSVs."""
    # ## Load Data

    data_dir = Path("raw_data")
    data_dir.mkdir(parents=True, exist_ok=True) # This document contains all two raw csv data

    pages_path = data_dir / "pages_export.csv"
    links_path = data_dir / "links_export.csv"

    print(pages_path.exists())
    print(links_path.exists())

    # Read first 5 rows because row data is very huge

    if pages_path.exists():
        pages = pd.read_csv(pages_path, nrows=5)
    else:
        pages = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "kutayahin/wikipedia-link-graph-100k",
                "pages_export.csv"
                )
        pages.to_csv(pages_path, index=False)


    if links_path.exists():
        links = pd.read_csv(links_path, nrows=5)
    else:
        links = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "kutayahin/wikipedia-link-graph-100k",
                "links_export.csv"
                )
        links.to_csv(links_path, index=False)


    print("pages:")
    print(pages)

    print("\nlinks:")
    print(links)

    print(pages.columns.tolist())
    print(links.columns.tolist())

    print(pages.dtypes)
    print(links.dtypes)

    # # Node Mapping

    # ## Check the unique of Data

    pages = pd.read_csv(
        pages_path,
        usecols=["id", "title", "language", "url"]
    )


    print(len(pages))

    print(pages['language'].value_counts())
    print(pages['language'].unique())

    print("Unique titles:", pages['title'].nunique())
    print("Duplicate titles:", pages['title'].duplicated().sum())
    print("Unique URLs:", pages["url"].nunique())
    print("Duplicate URLs:", pages["url"].duplicated().sum())

    # The result shows in the pages there are only English pages

    links_sample = pd.read_csv(
        links_path,
        usecols=["source_title", "target_title"],
        nrows=100000
    )

    print(links_sample.head())

    print("Unique source_titles:", links_sample["source_title"].nunique())
    print("Duplicate edges:", links_sample.duplicated(subset=["source_title", "target_title"]).sum())

    # ## Create Mapping

    title_to_idx = pd.Series(
        np.arange(len(pages)),
        index= pages['title']
    )

    print(title_to_idx.head())

    links_sample['source_idx'] = links_sample['source_title'].map(title_to_idx)
    links_sample['target_idx'] = links_sample['target_title'].map(title_to_idx)
    print(links_sample.head())

    source_match = links_sample['source_idx'].notna().mean()
    target_match = links_sample['target_idx'].notna().mean()

    both_match = (
        links_sample['source_idx'].notna() & links_sample['target_idx'].notna()
    )

    print("Source match:", source_match)
    print("Target match:", source_match)
    print("Both match:", source_match)

    # # Create Sparse Adjacency Matrix

    source = links_sample["source_idx"].to_numpy(dtype=np.int64)
    target = links_sample["target_idx"].to_numpy(dtype=np.int64)

    print(links_sample[["source_idx", "target_idx"]].isna().sum())

    links_url_sample = pd.read_csv(
        links_path,
        usecols=["target_url"],
        nrows=100_000
    )

    url_match = links_url_sample["target_url"].isin(
        pages["url"]
    )

    print("Target URL match rate:", url_match.mean())

    check = pd.read_csv(
        links_path,
        usecols=["target_title", "target_url"],
        nrows=100_000
    )

    title_match = check["target_title"].isin(pages["title"])
    url_match = check["target_url"].isin(pages["url"])

    print("Different matching results:",
          (title_match != url_match).sum())

    unmatched = links_sample[
        links_sample["target_idx"].isna()
    ]

    print(unmatched[
        ["source_title", "target_title"]
    ].head(10).to_string(index=False))

    valid_links = links_sample.dropna(
        subset=['source_idx','target_idx']
    ).copy()

    print("Original links:", len(links_sample))
    print("Valid links:", len(valid_links))
    print("Removed links:", len(links_sample) - len(valid_links))

    source = valid_links["source_idx"].to_numpy(dtype=np.int64)

    target = valid_links["target_idx"].to_numpy(dtype=np.int64)

    print(source[:5])
    print(target[:5])

    data = np.ones(len(source), dtype=np.float64)

    n = len(pages)

    A_csr = sparse.csr_matrix(
        (data, (target, source)),
        shape=(n,n)
    )

    # why csr: CSR didn't need iterate all zero elements in matrix
    # can directly find the non-zero elements in each row
    A_csr.sum_duplicates()
    A_csr.data[:] = 1.0

    print("Matrix shape:", A_csr.shape)
    print("Unique edges:", A_csr.nnz) #nnz: Number of Non-zero Entries

    # # Chunk processing

    total_links = 0
    valid_links = 0

    A_demo = sparse.csr_matrix((n,n), dtype=np.int32)

    reader = pd.read_csv(links_path, usecols=["source_title", "target_title"], chunksize=100000)

    for i, chunk in enumerate(islice(reader, 3), start=1):
        source_idx = chunk['source_title'].map(title_to_idx)
        target_idx = chunk['target_title'].map(title_to_idx)

        valid = source_idx.notna() & target_idx.notna()

        source = source_idx[valid].to_numpy(dtype=np.int32)
        target = target_idx[valid].to_numpy(dtype=np.int32)

        data = np.ones(len(source), dtype=np.int32)

        A_chunk = sparse.csr_matrix(
            (data,(target, source)),
            shape=(n,n)
        )

        A_demo = A_demo.maximum(A_chunk)

        total_links += len(chunk)
        valid_links += len(source)

        print(
            f"Chunk{i}:"
            f"read={len(chunk)},"
            f"valid={len(source)},"
            f"graph_edges={A_demo.nnz}"
        )

    print("Toal rows processed:",total_links)
    print("Valid link records:", valid_links)
    print("Unique internal edges:", A_demo.nnz)


    # Step 1: 读取 Pages 文件
    pages_check = pd.read_csv(
        pages_path,
        usecols=["title"]
    )

    # Step 2: 建立网页标题到整数索引的映射
    title_to_idx_check = pd.Series(
        np.arange(len(pages_check)),
        index=pages_check["title"]
    )

    # Step 3: 读取 Links 文件的前 100,000 行
    links_check = pd.read_csv(
        links_path,
        usecols=["source_title", "target_title"],
        nrows=100_000
    )

    # Step 4: 将网页标题映射成索引
    source_idx_check = links_check["source_title"].map(title_to_idx_check)
    target_idx_check = links_check["target_title"].map(title_to_idx_check)

    # Step 5: 判断 Source 和 Target 是否都能匹配
    valid_check = source_idx_check.notna() & target_idx_check.notna()

    # Step 6: 输出统计结果
    print("Total links:", len(links_check))
    print("Source unmatched:", source_idx_check.isna().sum())
    print("Target unmatched:", target_idx_check.isna().sum())
    print("Valid link records:", valid_check.sum())

    print("Original mapping size:", len(title_to_idx))
    print("Check mapping size:", len(title_to_idx_check))

    print(
        "Mapping keys identical:",
        title_to_idx.index.equals(title_to_idx_check.index)
    )

    print(
        "Mapping values identical:",
        np.array_equal(
            title_to_idx.to_numpy(),
            title_to_idx_check.to_numpy()
        )
    )

    # 使用旧映射
    source_old = links_check["source_title"].map(title_to_idx)
    target_old = links_check["target_title"].map(title_to_idx)

    valid_old = source_old.notna() & target_old.notna()

    print("Old mapping valid links:", valid_old.sum())

    # 使用新映射
    print("New mapping valid links:", valid_check.sum())

    # number of nodes
    n = len(pages)

    total_links = 0
    valid_links = 0

    # Create Node Mapping
    page_index_map = pd.Series(
        np.arange(n, dtype=np.int32),
        index=pages["title"].to_numpy()
    )

    # check Mapping
    assert page_index_map.min() == 0
    assert page_index_map.max() == n - 1
    assert page_index_map.nunique() == n

    # create two list for save valid
    source_parts = []
    target_parts = []

    reader = pd.read_csv(
        links_path,
        usecols = ['source_title','target_title'],
        chunksize=100000
    )

    for i, chunk in enumerate(reader, start=1):

        # Mapping
        source_idx = chunk['source_title'].map(page_index_map)
        target_idx = chunk['target_title'].map(page_index_map)

        # Filtering
        valid = source_idx.notna() & target_idx.notna()

        # Extract valid
        source = source_idx[valid].to_numpy(dtype=np.int32)
        target = target_idx[valid].to_numpy(dtype=np.int32)

        # save Chunk to lists
        if len(source) > 0:

            assert source.min() >= 0
            assert source.max() < n

            assert target.min() >= 0
            assert target.max() < n


            source_parts.append(source)
            target_parts.append(target)

        total_links += len(chunk)
        valid_links += len(source)

        # output every 10 chunks
        if i == 1 or i % 10 == 0:
            print(
                f"Chunk {i}",
                f"total={total_links:,},"
                f"valid={valid_links:,}"
            )

    print("Total rows processed:", total_links)
    print("Valid link recors:", valid_links)

    source_all = np.concatenate(source_parts)
    target_all = np.concatenate(target_parts)

    data = np.ones(len(source_all), dtype=np.int32)

    A = sparse.csr_matrix(
        (data, (target_all, source_all)),
        shape=(n,n)
    )

    A.sum_duplicates()

    A.data[:] = 1

    A.eliminate_zeros()

    print("Matrix shape:", A.shape)
    print("Valid link records:", valid_links)
    print("Unique internal edges:", A.nnz)
    print("Duplicate records:", valid_links - A.nnz)

    print("n =", n)
    print("Number of pages =", len(pages))

    print("Source minimum =", source_all.min())
    print("Source maximum =", source_all.max())

    print("Target minimum =", target_all.min())
    print("Target maximum =", target_all.max())

    print("Mapping size =", len(title_to_idx))
    print("Mapping maximum =", title_to_idx.max())

    # Calculate Out-degree
    out_degree = np.asarray(A.sum(axis=0)).ravel()

    # Identify  Dangling Nodes
    dangling = (out_degree == 0)

    # Display results
    print("Number of nodes:", len(out_degree))
    print("Total edges:", out_degree.sum())
    print("Average out-degree:", out_degree.mean())
    print("Maximum out-degree:", out_degree.max())
    print("Dangling nodes:", dangling.sum())
    print("Dangling ratio:", dangling.mean())

    # Inverse out-degree
    inv_degree = np.zeros(n, dtype=np.float64)

    np.divide(
        1.0,
        out_degree,
        out=inv_degree,
        where=(out_degree != 0)
    )

    # Construct normalized sparse matrix S
    S = A @ sparse.diags(inv_degree, format = 'csr')

    # Check matrix properties
    print('S shape:', S.shape)
    print('S nnz:', S.nnz)

    # Uniform personalization vector
    v = np.full(n, 1.0 / n)

    def apply_P(x):
        # Sparse matrix-vector multiplication
        y = S @ x

        # Probability mass currently at dangling nodes
        dangling_mass = x[dangling].sum()

        # Redistribute dangling mass
        y = y + dangling_mass * v

        return y

    # Column sums of S
    col_sums_S = np.asarray(S.sum(axis=0)).ravel()

    # Column sums of implicitly corrected P
    col_sums_P = col_sums_S + dangling.astype(np.float64)

    print(
        "All columns sum to 1:",
        np.allclose(col_sums_P, 1.0)
    )

    print(
        "Maximum column-sum error:",
        np.max(np.abs(col_sums_P - 1.0))
    )

    x = np.full(n, 1.0 / n)

    y = apply_P(x)

    print("Input probability sum:", x.sum())
    print("Output probability sum:", y.sum())
    print("Minimum output value:", y.min())

    return S, dangling, v
