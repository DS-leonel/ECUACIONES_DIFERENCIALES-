import sympy as sp

class EcuacionDiferencialSolver:
    """
    Clase encargada de la lógica matemática utilizando SymPy.
    Resuelve Ecuaciones Diferenciales Exactas y Reducibles a Exactas (Factor Integrante).
    """

    def __init__(self):
        # Definimos los símbolos matemáticos base
        self.x, self.y, self.C = sp.symbols('x y C')
        
    def resolver_exacta(self, M_str, N_str):
        """
        Resuelve M(x,y)dx + N(x,y)dy = 0.
        Retorna: (Solución LaTeX, Lista de diccionarios de pasos)
        """
        pasos = []
        
        # Función auxiliar para guardar cada paso
        def agregar_paso(titulo, explicacion, formula_latex):
            pasos.append({
                "titulo": titulo,
                "texto": explicacion,
                "formula": formula_latex
            })

        try:
            # 0. Limpieza y conversión
            # Eliminamos 'math.' por si la IA o el usuario lo escriben, ya que SymPy usa su propia sintaxis
            M_str = M_str.replace("math.", "").replace("Math.", "")
            N_str = N_str.replace("math.", "").replace("Math.", "")

            # Convertir texto a objetos SymPy
            M = sp.sympify(M_str)
            N = sp.sympify(N_str)
            
            # --- Paso 1: Verificar Exactitud ---
            dM_dy = sp.diff(M, self.y)
            dN_dx = sp.diff(N, self.x)
            
            check_latex = f"\\frac{{\\partial M}}{{\\partial y}} = {sp.latex(dM_dy)} \\quad \\text{{y}} \\quad \\frac{{\\partial N}}{{\\partial x}} = {sp.latex(dN_dx)}"
            
            agregar_paso(
                "1. Verificar Exactitud",
                "Calculamos las derivadas parciales cruzadas para verificar si es exacta.",
                check_latex
            )

            exacta = dM_dy.equals(dN_dx)

            # --- LÓGICA DE FACTOR INTEGRANTE (Si no es exacta) ---
            if not exacta:
                agregar_paso("No es Exacta", "Las derivadas son diferentes. Buscaremos un Factor Integrante (μ) para convertirla en exacta.", r"\frac{\partial M}{\partial y} \neq \frac{\partial N}{\partial x}")
                
                mu = None
                tipo_factor = ""

                # Caso A: Factor integrante depende solo de x: (My - Nx) / N
                factor_x = (dM_dy - dN_dx) / N
                factor_x = sp.simplify(factor_x)
                
                # Verificamos si factor_x no tiene 'y' (es solo de x o constante)
                if self.y not in factor_x.free_symbols:
                    mu = sp.exp(sp.integrate(factor_x, self.x))
                    tipo_factor = "x"
                    explicacion_mu = f"Encontramos que \\frac{{M_y - N_x}}{{N}} depende solo de x. El factor integrante es: \\mu(x) = e^{{\\int ({sp.latex(factor_x)}) dx}}"

                # Caso B: Factor integrante depende solo de y: (Nx - My) / M
                if mu is None:
                    factor_y = (dN_dx - dM_dy) / M
                    factor_y = sp.simplify(factor_y)
                    
                    if self.x not in factor_y.free_symbols:
                        mu = sp.exp(sp.integrate(factor_y, self.y))
                        tipo_factor = "y"
                        explicacion_mu = f"Encontramos que \\frac{{N_x - M_y}}{{M}} depende solo de y. El factor integrante es: \\mu(y) = e^{{\\int ({sp.latex(factor_y)}) dy}}"

                if mu is not None:
                    mu = sp.simplify(mu)
                    agregar_paso("1.1 Factor Integrante Hallado", explicacion_mu, f"\\mu = {sp.latex(mu)}")
                    
                    # Multiplicamos la ecuación original por mu
                    M = sp.simplify(M * mu)
                    N = sp.simplify(N * mu)
                    
                    agregar_paso("1.2 Nueva Ecuación Exacta", 
                                 "Multiplicamos M y N por el factor integrante (μ). Ahora la ecuación es exacta.", 
                                 f"\\tilde{{M}} = {sp.latex(M)}, \\quad \\tilde{{N}} = {sp.latex(N)}")
                else:
                    agregar_paso("Error", "No se encontró un factor integrante sencillo (dependiente solo de x o y).", r"\text{Método no aplicable}")
                    return None, pasos

            # --- RESOLUCIÓN DE LA ECUACIÓN EXACTA (Ya sea original o transformada) ---
            
            # Paso 2: Integrar M respecto a x
            F_xy_M_raw = sp.integrate(M, self.x)
            agregar_paso(
                "2. Integrar M respecto a x",
                "Integramos la función M (actual) con respecto a x. Añadimos g(y).",
                f"F(x, y) = \\int ({sp.latex(M)}) dx = {sp.latex(F_xy_M_raw)} + g(y)"
            )
            
            # Paso 3: Derivar F respecto a y
            dF_dy_raw = sp.diff(F_xy_M_raw, self.y)
            g_prime_expr = sp.simplify(N - dF_dy_raw)
            
            agregar_paso(
                "3. Encontrar g'(y)",
                "Derivamos el resultado anterior respecto a 'y' e igualamos a N. Despejamos g'(y).",
                f"g'(y) = N - \\frac{{\\partial F}}{{\\partial y}} = {sp.latex(g_prime_expr)}"
            )
            
            # Paso 4: Integrar g'(y)
            g_y = sp.integrate(g_prime_expr, self.y)
            agregar_paso(
                "4. Obtener g(y)",
                "Integramos g'(y) para hallar la función constante.",
                f"g(y) = \\int ({sp.latex(g_prime_expr)}) dy = {sp.latex(g_y)}"
            )
            
            # Paso 5: Solución Final
            solucion_simbolica = F_xy_M_raw + g_y
            # Intentar simplificar un poco la solución final
            solucion_simbolica = sp.simplify(solucion_simbolica)
            
            solucion_final_eq = sp.Eq(solucion_simbolica, self.C)
            
            agregar_paso(
                
                "5. Solución General",
                "Unimos las partes para formar la solución implícita F(x,y) = C.",
                sp.latex(solucion_final_eq)
            )
            
            return sp.latex(solucion_final_eq), pasos
            
        except Exception as e:
            pasos.append({"titulo": "Error Matemático", "texto": f"No se pudo procesar: {str(e)}", "formula": ""})
            return None, pasos