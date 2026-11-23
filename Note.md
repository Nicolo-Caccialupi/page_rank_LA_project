# Dangling-Node Correction and Stochasticity Verification

## Key terms

- **Damping parameter (阻尼系数)**: Used in the full PageRank model; it is not required for the dangling-node correction discussed below.
- **Stochasticity (随机性)**: The property that transition probabilities are nonnegative and sum to 1.
- **Dangling node (悬挂节点)**: A node without any outgoing links.

## 1. Dangling Nodes

A dangling node is a page without any outgoing links.

Example:

For a normal (non-dangling) page, its transition probabilities are:

$$
P_{ij} =
\begin{cases}
\dfrac{1}{d_j^{\mathrm{out}}}, & \text{if there is a link from page }j\text{ to page }i,\\
0, & \text{otherwise.}
\end{cases}
$$

Here, $d_j^{\mathrm{out}}$ is the out-degree of node $j$ (the number of outgoing links from $j$).

- Page A has two outgoing links, so the probability of moving from A to B or C is $1/2$ for each.
- Page C has no outgoing links, so the entire column corresponding to C is zero before correction.

### Column-Stochastic Convention (列随机约定)

For PageRank, we use a column-stochastic transition matrix. Each column represents the probabilities of leaving a source node, and every column must sum to 1:

$$
P_{ij}\ge 0, \qquad \sum_{i=1}^{n} P_{ij}=1 \quad \text{for all } j.
$$

**State transition matrix (状态转移矩阵)**: For $n$ possible states, the transition matrix has shape $n\times n$. Under this convention, $P_{ij}$ is the probability of moving from state $j$ to state $i$ in one step.

**Markov chain (马尔可夫链)**: The probability distribution of the next state depends only on the current state, not on the full history of previous states.

### How a Transition Matrix Acts on a PageRank Vector

Let $x$ be an $n\times 1$ probability vector. Its next-step distribution is $Px$. For a column-stochastic matrix $P$:

$$
\mathbf{1}^{T}(Px)=\mathbf{1}^{T}x.
$$

This means that multiplying by $P$ preserves the total probability.

## 2. Problem: A Dangling Column

For the example graph, before dangling-node correction the transition matrix is:

$$
S=\begin{bmatrix}
0 & 0 & 0\\
\frac{1}{2} & 0 & 0\\
\frac{1}{2} & 1 & 0
\end{bmatrix}.
$$

Check the column sums:

- Column A: $0+0.5+0.5=1$.
- Column B: $0+0+1=1$.
- Column C: $0+0+0=0$.

Column C does not sum to 1. After arriving at C, the matrix does not specify a valid next-step probability distribution.

Therefore, $S$ is not column-stochastic; it is column-substochastic (all entries are nonnegative, and each column sums to at most 1).

## 3. Fixing the Dangling-Node Problem

A basic correction is to replace every dangling column with a probability vector. With uniform personalization over three nodes:

$$
v=\begin{bmatrix}
\frac{1}{3}\\
\frac{1}{3}\\
\frac{1}{3}
\end{bmatrix}.
$$

The corrected transition matrix becomes:

$$
P=\begin{bmatrix}
0 & 0 & \frac{1}{3}\\
\frac{1}{2} & 0 & \frac{1}{3}\\
\frac{1}{2} & 1 & \frac{1}{3}
\end{bmatrix}.
$$

However, in a graph with many nodes, explicitly filling dangling columns creates many extra nonzero matrix entries. That can destroy the memory advantage of a sparse matrix.

The project therefore requires correcting dangling nodes without forming dense rank-one matrices.

### Dangling Indicator Vector

Define $d\in\mathbb{R}^n$ so that $d_j=1$ if node $j$ is dangling, and $d_j=0$ otherwise.

For this example:

$$
d=\begin{bmatrix}0\\0\\1\end{bmatrix}.
$$

The corrected matrix can be written mathematically as:

$$
\boxed{P=S+vd^{T}}
$$

The outer product $vd^{T}$ replaces each dangling column with $v$. We do not construct this outer product explicitly.

For any vector $x\in\mathbb{R}^n$, compute the product implicitly:

$$
\begin{aligned}
Px &= (S+vd^{T})x\\
   &= Sx+(vd^{T})x\\
   &= \boxed{Sx+v(d^{T}x)}.
\end{aligned}
$$

Why this is efficient:

- $Sx$ is a sparse matrix-vector product.
- $d^{T}x$ is a scalar: the total probability currently assigned to dangling nodes.
- $v(d^{T}x)$ distributes that probability according to the personalization vector.

Only the sparse matrix $S$ and the vectors $d$, $v$, and $x$ are needed.

## 4. Steps to Construct the Sparse Transition Matrix

### Step 1: Build the Adjacency Matrix

Use a sparse format such as COO to construct the adjacency matrix $A$.

Under our convention:

- Row $i$: Target node.
- Column $j$: Source node.
- $A_{ij}=1$ if there is a link from $j$ to $i$, and $0$ otherwise (for an unweighted graph).

### Step 2: Calculate Out-Degrees

The out-degree is the sum of the entries in each column:

$$
\boxed{d_j^{\mathrm{out}}=\sum_{i=1}^{n}A_{ij}}.
$$

### Step 3: Identify Dangling Nodes

$$
d_j=\begin{cases}
1, & d_j^{\mathrm{out}}=0,\\
0, & d_j^{\mathrm{out}}>0.
\end{cases}
$$

### Step 4: Normalize Non-Dangling Columns

For every node with $d_j^{\mathrm{out}}>0$, divide its column entries by its out-degree:

$$
S_{ij}=\begin{cases}
\dfrac{A_{ij}}{d_j^{\mathrm{out}}}, & d_j^{\mathrm{out}}>0,\\
0, & d_j^{\mathrm{out}}=0.
\end{cases}
$$

Thus, non-dangling columns sum to 1, while dangling columns remain zero in $S$.

### Step 5: Choose a Personalization Vector

The personalization vector $v$ must satisfy:

$$
v_i\ge 0,\qquad \sum_{i=1}^{n}v_i=1.
$$

For uniform personalization:

$$
v=\frac{1}{n}\mathbf{1}.
$$

Keep the normal columns unchanged and use $v$ to correct dangling columns:

$$
P=S+vd^T.
$$

### Step 6: Implement the Correction Implicitly

Instead of constructing $P$, perform each matrix-vector multiplication as:

$$
\boxed{Px=Sx+v(d^Tx)}.
$$

## 5. Verify Column Stochasticity Without Constructing P

A column-stochastic matrix must satisfy:

$$
P_{ij}\ge 0, \qquad \sum_i P_{ij}=1\quad \text{for every }j.
$$

Since $P=S+vd^T$, we have:

$$
\begin{aligned}
\sum_i P_{ij}
&=\sum_i S_{ij}+d_j\sum_i v_i\\
&=\sum_i S_{ij}+d_j,
\end{aligned}
$$

because $\sum_i v_i=1$.

Therefore, we can verify stochasticity without explicitly constructing $P$ by checking:

$$
\boxed{\sum_i S_{ij}+d_j=1\qquad\text{for every }j.}
$$

Two cases:

- Normal node: $\sum_i S_{ij}=1$ and $d_j=0$, so the result is $1$.
- Dangling node: $\sum_i S_{ij}=0$ and $d_j=1$, so the result is also $1$.

Because $S\ge 0$, $v\ge 0$, and $d\ge 0$, we also have $P\ge 0$ entrywise.

In vector notation, the same proof is:

$$
\mathbf{1}^{T}P
=\mathbf{1}^{T}S+(\mathbf{1}^{T}v)d^{T}
=\mathbf{1}^{T}S+d^{T}
=\mathbf{1}^{T}.
$$

**Conclusion**: The implicit dangling-node correction produces a valid column-stochastic transition matrix while preserving sparse storage.

> **Note**: Dangling-node correction and the PageRank damping parameter $\alpha$ solve different problems. After building $P$, the full PageRank model commonly uses $G=\alpha P+(1-\alpha)v\mathbf{1}^T$, which can also be applied implicitly without constructing a dense matrix.