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
@csrf_exempt # REMOVER EM PRODUÇÃO E USAR CSRF TOKEN NO AJAX
def api_registros_consumo(request):
    if request.method == 'GET':
        tipo_consumo = request.GET.get('tipo', None)
        if not tipo_consumo:
            return JsonResponse({'error': 'Parâmetro "tipo" é obrigatório'}, status=400)
        
        registros = RegistroConsumo.objects.filter(usuario=request.user, tipo=tipo_consumo).order_by('data', 'id')
        # Serializar os dados para JSON
        data = list(registros.values('id', 'tipo', 'consumo', 'apartamentos', 'consumo_por_apartamento', 'data', 'volume_inicial', 'volume_atual'))
        # Converter DateField para string
        for item in data:
            item['data'] = item['data'].strftime('%Y-%m-%d') if item['data'] else None
            # Garantir que floats sejam tratados corretamente (evitar None)
            item['consumo'] = item['consumo'] if item['consumo'] is not None else '-'
            item['apartamentos'] = item['apartamentos'] if item['apartamentos'] is not None else '-'
            item['consumo_por_apartamento'] = item['consumo_por_apartamento'] if item['consumo_por_apartamento'] is not None else '-'
            item['volume_inicial'] = item['volume_inicial'] if item['volume_inicial'] is not None else '-'
            item['volume_atual'] = item['volume_atual'] if item['volume_atual'] is not None else '-'

        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar dados recebidos (exemplo básico)
            tipo = data.get('tipo')
            consumo = data.get('consumo')
            apartamentos = data.get('apartamentos')
            consumo_por_apartamento = data.get('consumoPorApartamento')
            volume_inicial = data.get('volumeInicial')
            volume_atual = data.get('volumeAtual')

            if not tipo or tipo not in [choice[0] for choice in RegistroConsumo.TIPO_CHOICES]:
                return JsonResponse({'error': 'Tipo de consumo inválido ou ausente'}, status=400)

            # Função auxiliar para converter '-' ou None para None e string para float/int
            def clean_value(value, target_type=float):
                if value == '-' or value is None or value == '':
                    return None
                try:
                    return target_type(value)
                except (ValueError, TypeError):
                    return None # Ou lançar um erro se o valor for obrigatório e inválido

            registro = RegistroConsumo(
                usuario=request.user,
                tipo=tipo,
                consumo=clean_value(consumo),
                apartamentos=clean_value(apartamentos, int),
                consumo_por_apartamento=clean_value(consumo_por_apartamento),
                # Data é auto_now_add, não precisa ser passada aqui
                volume_inicial=clean_value(volume_inicial),
                volume_atual=clean_value(volume_atual)
            )
            registro.save()
            
            # Retornar o registro criado (opcional, mas útil para o frontend)
            response_data = {
                'id': registro.id,
                'tipo': registro.tipo,
                'consumo': registro.consumo if registro.consumo is not None else '-',
                'apartamentos': registro.apartamentos if registro.apartamentos is not None else '-',
                'consumo_por_apartamento': registro.consumo_por_apartamento if registro.consumo_por_apartamento is not None else '-',
                'data': registro.data.strftime('%Y-%m-%d'),
                'volume_inicial': registro.volume_inicial if registro.volume_inicial is not None else '-',
                'volume_atual': registro.volume_atual if registro.volume_atual is not None else '-'
            }
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            # Logar o erro real em um sistema de logging
            print(f"Erro ao salvar registro: {e}") 
            return JsonResponse({'error': 'Erro interno ao salvar registro'}, status=500)

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

@login_required
@require_http_methods(["POST"]) 
@csrf_exempt # REMOVER EM PRODUÇÃO E USAR CSRF TOKEN NO AJAX
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

        # Aqui, em vez de salvar no localStorage, poderíamos salvar em um model separado 
        # ou talvez atualizar o último registro existente se fizer sentido, 
        # ou ainda ter um campo específico no perfil do usuário.
        # Por simplicidade, vamos apenas retornar sucesso, assumindo que o frontend 
        # usará essa informação temporariamente ou a enviará junto com o próximo registro.
        # Uma abordagem mais robusta seria salvar isso no banco.
        # Exemplo: Atualizar um campo 'ultimo_volume_inicial' no perfil do usuário
        # request.user.profile.update_volume_inicial(tipo_consumo, volume_inicial_float)
        
        # *** Implementação Simplificada: Apenas confirma recebimento ***
        # O frontend precisará gerenciar como usar esse valor.
        # Idealmente, isso seria salvo no backend de forma persistente.

        # Criando um registro inicial apenas com o volume?
        # Ou apenas armazenando para usar no próximo cálculo?
        # Vamos criar um registro especial para marcar o início?
        # Por ora, vamos apenas retornar sucesso.
        # TODO: Definir como persistir o volume inicial de forma robusta no backend.

        return JsonResponse({'success': True, 'message': f'Volume inicial {volume_inicial_float:.2f} para {tipo_consumo} recebido.'})

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



def api_registros_rvn(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo')
        registros = ConsumoRVN.objects.filter(tipo=tipo).values()
        return JsonResponse(list(registros), safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        registro = ConsumoRVN.objects.create(
            tipo=data.get('tipo'),
            consumo=data.get('consumo'),
            apartamentos=data.get('apartamentos'),
            consumo_por_apartamento=data.get('consumo_por_apartamento'),
            volume_inicial=data.get('volumeInicial'),
            volume_atual=data.get('volumeAtual')
        )
        return JsonResponse({
            "id": registro.id,
            "tipo": registro.tipo,
            "consumo": str(registro.consumo),
            "apartamentos": registro.apartamentos,
            "consumo_por_apartamento": str(registro.consumo_por_apartamento),
            "data": registro.data.strftime('%Y-%m-%d'),
            "volume_inicial": str(registro.volume_inicial),
            "volume_atual": str(registro.volume_atual)
        })

@csrf_exempt
def remover_ultimo_rvn(request):
    if request.method == 'POST':
        tipo = json.loads(request.body).get('tipo')
        ultimo = ConsumoRVN.objects.filter(tipo=tipo).last()
        if ultimo:
            ultimo.delete()
            return JsonResponse({'success': True, 'message': 'Último registro removido.'})
        return JsonResponse({'success': False, 'message': 'Nenhum registro encontrado.'})

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
    


