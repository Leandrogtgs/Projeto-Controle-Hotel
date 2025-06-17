from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt # Consider using proper CSRF handling for AJAX
import json
from .models import RegistroConsumo

from .models import ConsumoRVN

from django.views.decorators.http import require_POST
from django.contrib.auth import logout

# View para a página inicial (sem alterações necessárias por enquanto)
@login_required
def pagina_inicial(request):
    return render(request, 'minha_pagina/pagina_inicial.html')

# View para a página de consumo de água (CRB)
@login_required
def consumo_crb(request):
    # Simplesmente renderiza o template. A lógica de dados será via AJAX.
    return render(request, 'minha_pagina/consumo_crb.html')

# View para a página de consumo de gás
@login_required
def consumo_gas(request):
    # Simplesmente renderiza o template. A lógica de dados será via AJAX.
    return render(request, 'minha_pagina/consumo_gas.html')

# View para a página de consumo de energia
@login_required
def consumo_energia(request):
    # Simplesmente renderiza o template. A lógica de dados será via AJAX.
    return render(request, 'minha_pagina/consumo_energia.html')

# --- Views AJAX para manipulação de dados de consumo ---

@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt  # REMOVER EM PRODUÇÃO
def api_registros_consumo(request):
    if request.method == "GET":
        tipo_consumo = request.GET.get("tipo")
        if not tipo_consumo:
            return JsonResponse({"error": "Parâmetro 'tipo' é obrigatório"}, status=400)

        registros = RegistroConsumo.objects.filter(
            usuario=request.user, tipo=tipo_consumo
        ).order_by("data", "id")

        data = []
        for r in registros:
            # Calcula consumo_total na hora da consulta, caso não esteja salvo no BD
            consumo_total = None
            if r.volume_atual is not None and r.volume_inicial is not None:
                consumo_total = r.volume_atual - r.volume_inicial

            data.append({
                "id": r.id,
                "tipo": r.tipo,
                "consumo": r.consumo or "-",
                "apartamentos": r.apartamentos or "-",
                "consumo_por_apartamento": r.consumo_por_apartamento or "-",
                "volume_inicial": r.volume_inicial or "-",
                "volume_atual": r.volume_atual or "-",
                "botija_01": r.botija_01 or "-",
                "botija_02": r.botija_02 or "-",
                "botija_03": r.botija_03 or "-",
                "botija_04": r.botija_04 or "-",
                "hospedes": r.hospedes or "-",
                "consumo_total": consumo_total if consumo_total is not None else "-",
                "data": r.data.strftime("%Y-%m-%d") if r.data else None,
            })

        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        try:
            dados = json.loads(request.body)

            def clean(val, tipo=float):
                if val in ("", "-", None):
                    return None
                try:
                    return tipo(val)
                except:
                    return None

            volume_inicial = clean(dados.get("volumeInicial"))
            volume_atual = clean(dados.get("volumeAtual"))

            consumo_total = volume_atual - volume_inicial if volume_atual is not None and volume_inicial is not None else None

            registro = RegistroConsumo.objects.create(
                usuario=request.user,
                tipo=dados.get("tipo"),
                consumo=clean(dados.get("consumo")),
                apartamentos=clean(dados.get("apartamentos"), int),
                consumo_por_apartamento=clean(dados.get("consumoPorApartamento")),
                volume_inicial=volume_inicial,
                volume_atual=volume_atual,
                botija_01=clean(dados.get("botija_01")),
                botija_02=clean(dados.get("botija_02")),
                botija_03=clean(dados.get("botija_03")),
                botija_04=clean(dados.get("botija_04")),
                hospedes=clean(dados.get("hospedes"), int),
                consumo_total=consumo_total,
            )

            return JsonResponse({
                "id": registro.id,
                "tipo": registro.tipo,
                "consumo": registro.consumo or "-",
                "apartamentos": registro.apartamentos or "-",
                "consumo_por_apartamento": registro.consumo_por_apartamento or "-",
                "volume_inicial": registro.volume_inicial or "-",
                "volume_atual": registro.volume_atual or "-",
                "botija_01": registro.botija_01 or "-",
                "botija_02": registro.botija_02 or "-",
                "botija_03": registro.botija_03 or "-",
                "botija_04": registro.botija_04 or "-",
                "hospedes": registro.hospedes or "-",
                "consumo_total": registro.consumo_total or "-",
                "data": registro.data.strftime("%Y-%m-%d"),
            }, status=201)

        except Exception as e:
            print(f"Erro: {e}")
            return JsonResponse({"error": "Erro ao salvar"}, status=500)




@login_required
@require_http_methods(["POST"]) # Usando POST para simplicidade, idealmente seria DELETE
@csrf_exempt # REMOVER EM PRODUÇÃO E USAR CSRF TOKEN NO AJAX
def api_remover_ultimo_registro(request):
    try:
        data = json.loads(request.body)
        tipo_consumo = data.get('tipo')
        if not tipo_consumo:
            return JsonResponse({'error': 'Parâmetro "tipo" é obrigatório'}, status=400)

        ultimo_registro = RegistroConsumo.objects.filter(usuario=request.user, tipo=tipo_consumo).order_by('-data', '-id').first()
        if ultimo_registro:
            ultimo_registro.delete()
            return JsonResponse({'success': True, 'message': 'Último registro removido com sucesso.'})
        else:
            return JsonResponse({'success': False, 'message': 'Nenhum registro encontrado para remover.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"Erro ao remover registro: {e}")
        return JsonResponse({'error': 'Erro interno ao remover registro'}, status=500)

@login_required
@require_http_methods(["POST"]) # Usando POST para simplicidade
@csrf_exempt # REMOVER EM PRODUÇÃO E USAR CSRF TOKEN NO AJAX
def api_limpar_registros(request):
    try:
        data = json.loads(request.body)
        tipo_consumo = data.get('tipo')
        if not tipo_consumo:
            return JsonResponse({'error': 'Parâmetro "tipo" é obrigatório'}, status=400)

        registros_removidos, _ = RegistroConsumo.objects.filter(usuario=request.user, tipo=tipo_consumo).delete()
        if registros_removidos > 0:
            return JsonResponse({'success': True, 'message': f'{registros_removidos} registros removidos com sucesso.'})
        else:
            return JsonResponse({'success': False, 'message': 'Nenhum registro encontrado para limpar.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"Erro ao limpar registros: {e}")
        return JsonResponse({'error': 'Erro interno ao limpar registros'}, status=500)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import RegistroConsumo  # ajuste conforme o nome do seu modelo
import json

@csrf_exempt  # REMOVER EM PRODUÇÃO
@login_required
@require_http_methods(["POST"])
def api_registrar_volume_inicial(request):
    try:
        data = json.loads(request.body)
        tipo_consumo = data.get('tipo')
        volume_inicial = data.get('volumeInicial')

        if not tipo_consumo or tipo_consumo not in ['Água', 'Gás', 'Eletricidade']:
            return JsonResponse({'error': 'Tipo de consumo inválido ou não suportado para volume inicial.'}, status=400)

        try:
            volume_inicial_float = float(volume_inicial)
            if volume_inicial_float < 0:
                raise ValueError("Volume inicial não pode ser negativo.")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Volume inicial inválido.'}, status=400)

        # Cria o registro com volume inicial
        registro = RegistroConsumo.objects.create(
            tipo=tipo_consumo,
            volume_inicial=volume_inicial_float,
            volume_atual=volume_inicial_float,
            consumo=None,
            apartamentos=None,
            consumo_por_apartamento=None,
            usuario=request.user
        )

        return JsonResponse({
            'success': True,
            'registro': {
                'id': registro.id,
                'tipo': registro.tipo,
                'consumo': '-' if registro.consumo is None else f"{registro.consumo:.2f}",
                'apartamentos': '-' if registro.apartamentos is None else registro.apartamentos,
                'consumo_por_apartamento': '-' if registro.consumo_por_apartamento is None else f"{registro.consumo_por_apartamento:.2f}",
                'data': registro.data.strftime('%Y-%m-%d'),
                'volume_inicial': f"{registro.volume_inicial:.2f}",
                'volume_atual': f"{registro.volume_atual:.2f}"
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"Erro ao registrar volume inicial: {e}")
        return JsonResponse({'error': 'Erro interno ao registrar volume inicial'}, status=500)

@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect('minha_pagina:login')







# View para a página de consumo de água (rvn)
@login_required
def consumo_rvn(request):
    # Simplesmente renderiza o template. A lógica de dados será via AJAX.
    return render(request, 'minha_pagina/consumo_rvn.html')

# View para a página de consumo de gás (rvn)
@login_required
def consumo_gas_rvn(request):
    # Simplesmente renderiza o template. A lógica de dados será via AJAX.
    return render(request, 'minha_pagina/consumo_gas_rvn.html')


# View para a página de consumo de energia (rvn)
@login_required
def consumo_energia_rvn(request):
    # Simplesmente renderiza o template. A lógica de dados será via AJAX.
    return render(request, 'minha_pagina/consumo_energia_rvn.html')



@login_required
def consumo_rvn_view(request):
    return render(request, 'minha_pagina/consumo_rvn.html')


@login_required
def consumo_energia_rvn_view(request):
    return render(request, 'minha_pagina/consumo_energia_rvn.html')



@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_registros_rvn(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo')
        registros = ConsumoRVN.objects.filter(tipo=tipo).order_by("data", "id")
        data = []

        for r in registros:
            # Obtém volume_inicial e volume_atual convertidos para float (ou None)
            try:
                volume_inicial = float(r.volume_inicial) if r.volume_inicial is not None else None
            except:
                volume_inicial = None

            try:
                volume_atual = float(r.volume_atual) if r.volume_atual is not None else None
            except:
                volume_atual = None

            if volume_inicial is not None and volume_atual is not None:
                consumo_total = volume_atual - volume_inicial
                consumo_total_str = f"{consumo_total:.2f}"
            else:
                consumo_total_str = "-"

            data.append({
                "id": r.id,
                "tipo": r.tipo,
                "consumo": str(r.consumo) if r.consumo is not None else "-",
                "apartamentos": r.apartamentos or "-",
                "consumo_por_apartamento": str(r.consumo_por_apartamento) if r.consumo_por_apartamento is not None else "-",
                "volume_inicial": str(r.volume_inicial) if r.volume_inicial is not None else "-",
                "volume_atual": str(r.volume_atual) if r.volume_atual is not None else "-",
                "botija_01": str(r.botija_01) if r.botija_01 is not None else "-",
                "botija_02": str(r.botija_02) if r.botija_02 is not None else "-",
                "hospedes": r.hospedes or "-",
                "data": r.data.strftime('%Y-%m-%d'),
                "consumo_total": consumo_total_str,
            })

        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)

            def clean(val, tipo=float):
                if val in ("", "-", None):
                    return None
                try:
                    return tipo(val)
                except:
                    return None

            volume_inicial_val = clean(data.get('volumeInicial'))
            volume_atual_val = clean(data.get('volumeAtual'))

            registro = ConsumoRVN.objects.create(
                tipo=data.get('tipo'),
                consumo=clean(data.get('consumo')),
                apartamentos=clean(data.get('apartamentos'), int),
                consumo_por_apartamento=clean(data.get('consumo_por_apartamento')),
                volume_inicial=volume_inicial_val,
                volume_atual=volume_atual_val,
                botija_01=clean(data.get("botija_01")),
                botija_02=clean(data.get("botija_02")),
                hospedes=clean(data.get("hospedes"), int),
            )

            # Calcula consumo_total no POST também
            if volume_inicial_val is not None and volume_atual_val is not None:
                consumo_total_post = volume_atual_val - volume_inicial_val
                consumo_total_post_str = f"{consumo_total_post:.2f}"
            else:
                consumo_total_post_str = "-"

            return JsonResponse({
                "id": registro.id,
                "tipo": registro.tipo,
                "consumo": str(registro.consumo or "-"),
                "apartamentos": registro.apartamentos or "-",
                "consumo_por_apartamento": str(registro.consumo_por_apartamento or "-"),
                "volume_inicial": str(registro.volume_inicial or "-"),
                "volume_atual": str(registro.volume_atual or "-"),
                "botija_01": str(registro.botija_01 or "-"),
                "botija_02": str(registro.botija_02 or "-"),
                "hospedes": registro.hospedes or "-",
                "data": registro.data.strftime('%Y-%m-%d'),
                "consumo_total": consumo_total_post_str,
            }, status=201)

        except Exception as e:
            print("Erro ao salvar:", e)
            return JsonResponse({"error": "Erro ao salvar dados"}, status=500)


@csrf_exempt
def remover_ultimo_rvn(request):
    if request.method == 'POST':
        tipo = json.loads(request.body).get('tipo')
        if not tipo:
            return JsonResponse({'success': False, 'message': 'Tipo não informado.'})
        
        ultimo = ConsumoRVN.objects.filter(tipo=tipo).order_by('-data', '-id').first()
        if ultimo:
            ultimo.delete()
            return JsonResponse({'success': True, 'message': 'Último registro removido com sucesso.'})
        return JsonResponse({'success': False, 'message': 'Nenhum registro encontrado para remover.'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)

@csrf_exempt
def limpar_tudo_rvn(request):
    if request.method == 'POST':
        tipo = json.loads(request.body).get('tipo')
        ConsumoRVN.objects.filter(tipo=tipo).delete()
        return JsonResponse({'success': True, 'message': f'Todos os registros de {tipo} foram removidos.'})

@csrf_exempt
def registrar_volume_inicial_rvn(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tipo = data.get('tipo')
        volume = data.get('volumeInicial')

        if tipo and volume:
            registro = ConsumoRVN.objects.create(
                tipo=tipo,
                consumo=None,
                apartamentos=None,
                consumo_por_apartamento=None,
                volume_inicial=volume,
                volume_atual=volume
            )
            return JsonResponse({
                "success": True,
                "registro": {
                    "id": registro.id,
                    "tipo": registro.tipo,
                    "consumo": "-",
                    "apartamentos": "-",
                    "consumo_por_apartamento": "-",
                    "data": registro.data.strftime('%Y-%m-%d'),
                    "volume_inicial": str(registro.volume_inicial),
                    "volume_atual": str(registro.volume_atual)
                }
            })
        return JsonResponse({'success': False, 'message': 'Dados incompletos'}, status=400)
    


