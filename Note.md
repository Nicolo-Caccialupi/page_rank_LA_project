### Dangling-Node Correction and Stochasticity Verification

Damping parameter(阻尼系数)
stochasticity(随机性)
Dangling Nodes（悬挂节点）


#### Dangling Node

**without any Outgoing Links(出链)**

Example:
![1a3c83c7628f7ca6bb1552ed8d219a26](https://i.mji.rip/2026/11/22/0ab114f3b93ab530d1b37093168e6207.png)



for normal page, we can calculate it's transfer probability:

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

A has two Outgoing Links, so the probability that A transform to B and C is 0.5 in individual.

C doesn't has any Outgoing Links, so the whole column which it corresponded is 0.

**Column-Stochastic Convention**
在构建++状态转移矩阵++（如马尔可夫链、PageRank 算法）时，规定矩阵的每一列元素之和等于 1（且所有元素非负）


**状态转移矩阵（State Transition Matrix，通常记为 P 或 M）**

是用来描述一个系统在不同状态之间切换概率的二维数字表格，是马尔可夫链（Markov Chain）的核心工具。

矩阵结构： 有n个可能状态，状态转移矩阵就是一个nxn的矩阵
矩阵中的元素代表：从某个状态经过一步操作之后得到另一个状态的概率

**Markov Chain**
the next state of the system, only depend on the current state, don't depend on other state it experienced before.

**How Transiion Matrix work on PageRank Vector**


```math
\mathbf{1}^T(Px)=\mathbf{1}^Tx
```


#### Problem
After correlation:

```math

S=
\begin{bmatrix}
0&0&0\\
0.5&0&0\\
0.5&1&0
\end{bmatrix}

```

We imple ++Column-Stochastic Convention++(列随机约定):

Col A : 0 + 0.5 + 0.5 = 1
Col B : 0 + 0 + 1 = 1
Col C : 0 + 0 + 0 = 0

the sum of probability of Col c is 0, not 1, in Markov Chain, it means after reaching C, it doesn't define the next step.

So S is not the Column Stochastic Matrix, is the Column-Substochastic Matrix

#### Fix the Problem(fix the Dangling Node)

Basic method: Using random rate to fill the column in matrix

```math

P=
\begin{bmatrix}
0&0&1/3\\
1/2&0&1/3\\
1/2&1&1/3
\end{bmatrix}
```

But if the matrix has huge number of node, and contains lots of DanglingNodes, each column needs to fill no-zero probability.

this will generate huge amount of extra elements of matrix

According to the request: ++*without forming dense rank-one matrices*++

定义Dangling Indicator Vector:

d = [0 0 1]^T then: P = S + vd^T

for any variant x : Px = Sx + v(d^t x)

we need to realize:
```math
P=S+vd^T
```
but can't let it be dense matrix, so:

```math
{Px=Sx+v(d^Tx)}
```
#### Step to construct Sparse Transition Matrix, recognize Dangling Nodes

**Step1**:Build Adjacent Matrix
we can use COO matrix

**Step2**:Calculate Out-degree

(The sum of every column)
```math
d_j^{out}=\sum_{i=1}^{n}A_{ij}
```

**Step3**: Recognize Dangling Nodes

```math
d_j=
\begin{cases}
1 & d_j^{out}=0\\
0 & d_j^{out}>0
\end{cases}
```

**Step4**:Normalize

实现隐式Dangling Node Correction

#### Verify sticgastucuty
Column-Stochastic Marix必须满足L
P_ij >= 0 and Σp_ij = 1

because:

```math
P=S+vd^T
```
so:
```math
{\mathbf1^TP=\mathbf1^TS+(\mathbf1^Tv)d^T}
```

if v is alread normalized, then 1^t v = 1

so we need to check column sum of S + d_j = 1

**Implicit Dangling-Node Correction**

## 1.Adjacency Matrix

Row: Target
Col : Source

## 2.Out-degree

\[
{q_j=\sum_i A_{ij}}
\]

## 3.Normalization

Dangling Node don't have out-degree, so the column can't form the transform probability distribution

## 4.Dangling Nodes

we need to use the Personalization Vector(now is Uniform Personalization)
to help Dangling Node have same probabilities to other nodes

Personalization Vector must satisfy:

\[
v_i\geq0,\qquad\sum_i v_i=1
\]


also we need Dangling Indicator Vector to know which node is Dangling Nodes.


## 5. Dangling-Node Correction:

\[
{P=S+vd^T}
\]

keep the columns of normal node,
and use V to change the column of Dangling Node

## 6. Implicit Implementation
(Implicit Matrix-Vector Multiplication)

\[
P=S+vd^T
\]

\[
Px=(S+vd^T)x
\]

\[
Px=Sx+(vd^T)x
\]


\[
{Px=Sx+v(d^Tx)}
\]

## 7.Column Stochasticity

Column-Stochastic Matrix satisfy:

\[
{P_{ij}\geq0}
\]

\[
{\sum_iP_{ij}=1\qquad\forall j}
\]

proof without construct P

\[
\sum_iP_{ij}
=
\sum_iS_{ij}+d_j\sum_iv_i
\]


because:

\[
\sum_iv_i=1
\]

so：
\[
\boxed{\sum_iP_{ij}=\sum_iS_{ij}+d_j}
\]

As Normal Node:
The column of S =1, dj = 0

As Dangling Node:
The column of S =0, dj = 1

















