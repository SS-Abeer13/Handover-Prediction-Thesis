import re

def polish_math(text):
    text = text.replace('\u0303', '')  # remove stray combining tildes
    text = text.replace('\u0302', '')  # remove stray combining hats
    # fix lambda tildes
    text = re.sub(r'\$\\lambda\$\s*̃', r'$\\tilde{\\lambda}$', text)
    text = re.sub(r'\\lambdã', r'\\tilde{\\lambda}', text)
    text = re.sub(r'\$\\tilde\{\\lambda\}\$\\_k', r'$\\tilde{\\lambda}_k$', text)
    text = re.sub(r'\$\\lambda\$\\_k', r'$\\lambda_k$', text)
    text = re.sub(r'\bF\\_k\b', r'$F_k$', text)
    text = re.sub(r'\bS\\_k\b', r'$S_k$', text)
    text = re.sub(r'\(1\+\$\\epsilon\$\)\^k', r'$(1+\\epsilon)^k$', text)
    text = re.sub(r'\$\(1\+\\epsilon\)\$\^k', r'$(1+\\epsilon)^k$', text)
    text = re.sub(r'\$\(1\+\\epsilon\)\$\^k\$\$', r'$(1+\\epsilon)^k$', text)
    return text

sample = r"Writing the reweighted hazards as $\lambda$̃\_k $\approx$ w $\lambda$\_k for small $\lambda$\_k, error $\epsilon$ grows as (1+$\epsilon$)^k with the horizon. relative distortion of F\_k is bounded by w"
print(polish_math(sample))
