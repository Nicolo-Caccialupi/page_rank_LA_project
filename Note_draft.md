### Dangling-Node Correction and Stochasticity Verification

Damping parameter(阻尼系数)
stochasticity(随机性)
Dangling Nodes（悬挂节点）


#### Dangling Node

**without any Outgoing Links(出链)**

Example:
![1a3c83c7628f7ca6bb1552ed8d219a26](https://i.mji.rip/2026/11/22/0ab114f3b93ab530d1b37093168e6207.png)



for a normal page, we can calculate its transition probability as follows:

```math
P_{ij}=
\begin{cases}
\frac{1}{d_j^{out}} & \text{if page }j\text{ to }i\\
0 & \text{else}
\end{cases}
```


```math
d_j^{out} \text{ is the Out-degree of j}
```

Page A has two Outgoing Links, so the transition probability from A transform to either B or C is 0.5.

C has no Outgoing Links, so its corresponding column in the transition matrix contains only zeros

**Column-Stochastic Convention**
在构建++状态转移矩阵++（如马尔可夫链、PageRank 算法）时，规定矩阵的每一列元素之和等于 1（且所有元素非负）

When constructing a column-stochastic Transition Matrix, we require all entries to be non-negative and the sum of each column to equal 1 


**状态转移矩阵（State Transition Matrix，通常记为 P 或 M）**

是用来描述一个系统在不同状态之间切换概率的二维数字表格，是马尔可夫链（Markov Chain）的核心工具。

矩阵结构： 有n个可能状态，状态转移矩阵就是一个nxn的矩阵
矩阵中的元素代表：从某个状态经过一步操作之后得到另一个状态的概率

it desceibes the probabilities of moving between different states of a system

Matrix structure:  For a system with n possible states, the transition matrix is a nxn matrix

the meaning of the element in matrix:

the probability of moving from one state to another state in a single step

**Markov Chain**
the next state of the system, only depends on the current state, not on the sequence of previous states

**How Transiion Matrix work on PageRank Vector**


```math
\mathbf{1}^T(Px)=\mathbf{1}^Tx
```


#### Problem
Before correlation:

```math

S=
\begin{bmatrix}
0&0&0\\
0.5&0&0\\
0.5&1&0
\end{bmatrix}

```

We adopt the ++Column-Stochastic Convention++(列随机约定):

Col A : 0 + 0.5 + 0.5 = 1
Col B : 0 + 0 + 1 = 1
Col C : 0 + 0 + 0 = 0

the sum of the entries in column C is 0 rather than 1, in Markov Chain, this means that the transition probabilities from node C are not defined

Therefore,  S is not the Column Stochastic Matrix, Instead it is the Column-Substochastic Matrix

#### Fix the Problem(fix the Dangling Node)

Basic method: replacing each dangling column with a uniform proability distrbituion

```math

P=
\begin{bmatrix}
0&0&1/3\\
1/2&0&1/3\\
1/2&1&1/3
\end{bmatrix}
```

But if the graph contains a large number of nodes and lots of DanglingNodes, each dangling column must be filled with no-zero transition probabilities.

This introduces a large number of additional non-zero entries into the matrix

According to the request: ++*without explicitly forming dense rank-one matrices*++

定义Dangling Indicator Vector:

d = [0 0 1]^T then: P = S + vd^T

for any vector x : Px = Sx + v(d^t x)

we need to implement:
```math
P=S+vd^T
```
we must avoid explicitly constructing the dense corrected matrix, so:

```math
{Px=Sx+v(d^Tx)}
```
#### Step to construct Sparse Transition Matrix, recognize Dangling Nodes

**Step1**:Construct the Adjacent Matrix
we can use the COO sparse matrix format

**Step2**:Compute the Out-degree

(The sum of the entries in each column)
```math
d_j^{out}=\sum_{i=1}^{n}A_{ij}
```

**Step3**: Identify Dangling Nodes

```math
d_j=
\begin{cases}
1 & d_j^{out}=0\\
0 & d_j^{out}>0
\end{cases}
```

**Step4**:Normalize the None Dangling Columns

实现隐式Dangling Node Correction

#### Verify stochasticity

Column-Stochastic Marix must satisfy the following two conditions:
P_ij >= 0 and Σp_ij = 1

because:
```math
P=S+vd^T
```
so:
```math
{\mathbf1^TP=\mathbf1^TS+(\mathbf1^Tv)d^T}
```

since v is alread normalized, then 1^t v = 1

therefore, we only need to verify that the sum of column j in S + d_j = 1

**Implicit Dangling-Node Correction**



## 1.Adjacency Matrix

Row: Target
Col : Source

## 2.Out-degree


```math
\
{q_j=\sum_i A_{ij}}
\
```

## 3.Normalization

Dangling Nodes have an out degree of zero, therefore their corresponding columns do not define valid probability distributions

## 4.Dangling Nodes

we use a Personalization Vector, choosing a uniform distribution in this implementation, this assigns equal transition probabilities to all possible destination nodes for each dangling node

Personalization Vector must satisfy:


```math
\
v_i\geq0,\qquad\sum_i v_i=1
\
```



we also use dangling node indicator vector to identify which nodes have no outgoing links


## 5. Dangling-Node Correction:

```math
\
{P=S+vd^T}
\
```


We preserve the columns corresponing to no-dangling nodes,
and use the vector v to replace the columns corresponding to dangling nodes

## 6. Implicit Implementation
(Implicit Matrix-Vector Multiplication)


```math
\
P=S+vd^T
\
```



```math
\
Px=(S+vd^T)x
\
```



```math
\
Px=Sx+(vd^T)x
\
```




```math
\
{Px=Sx+v(d^Tx)}
\
```


## 7.Column Stochasticity

A Column-Stochastic Matrix satisfies:


```math
\
{P_{ij}\geq0}
\
```



```math
\
{\sum_iP_{ij}=1\qquad\forall j}
\
```


prove column stochasticity without explicitly constructing P


```math
\
\sum_iP_{ij}
=
\sum_iS_{ij}+d_j\sum_iv_i
\
```



because:


```math
\
\sum_iv_i=1
\
```


so：

```math
\
{\sum_iP_{ij}=\sum_iS_{ij}+d_j}
\
```


For a non-dangling node:
The corresponding column of S sums to 1, and dj = 0

As Dangling Node:
The corresponding column of S sums to 0, and dj = 1














