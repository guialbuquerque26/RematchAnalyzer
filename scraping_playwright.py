"""
Scraping dinâmico usando Playwright para capturar dados do RematchTracker
Captura informações que só aparecem após JavaScript carregar (A+, Playing Style, etc.)
"""

import asyncio
import json
import re
import time
from playwright.async_api import async_playwright

async def scraping_dinamico_rematch(steam_id):
    """
    Faz scraping dinâmico da página do RematchTracker
    Captura: Grade (A+), Playing Style Analysis, tipo de jogador, etc.
    """
    url = f"https://www.rematchtracker.com/player/steam/{steam_id}"
    
    async with async_playwright() as p:
        browser = None
        try:
            print(f"🎭 Iniciando Playwright para Steam ID: {steam_id}")
            
            # Configurar navegador
            browser = await p.chromium.launch(
                headless=True,  # True = não mostra janela
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Criar nova página com configurações
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            print(f"📡 Acessando: {url}")
            
            # Navegar para a página
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            print("⏳ Aguardando elementos dinâmicos carregarem...")
            
            # Aguardar carregamento genérico da página
            print("⏳ Aguardando página carregar completamente...")
            await page.wait_for_timeout(8000)  # Aguardar 8 segundos para carregamento
            
            print("📊 Capturando dados dinâmicos...")
            
            # Estrutura de dados para capturar
            dados_dinamicos = {
                'steam_id': steam_id,
                'url': url,
                'captured_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'method': 'playwright_dynamic',
                'status': 'success',
                
                # Informações do jogador
                'player_info': {
                    'display_name': None,
                    'grade': None,        # A+, B+, etc.
                    'player_type': None,  # Impact Player, etc.
                    'rank': None          # Elite, Expert, etc.
                },
                
                # Análise de estilo de jogo (/100)
                'playing_style_analysis': {
                    'attack': None,
                    'playmaking': None,
                    'finishing': None,
                    'defense': None,
                    'goalkeeper': None,
                    'impact': None
                },
                
                # Estatísticas extras da página
                'page_stats': {
                    'win_rate_percent': None,
                    'shot_accuracy_percent': None,
                    'mvp_rate_percent': None,
                    'steals_total': None,
                    'tackles_total': None
                },
                
                # Elementos raw encontrados (debug)
                'raw_elements': {},
                'full_page_text': None
            }
            
            # Capturar todo o conteúdo da página
            page_content = await page.content()
            page_text = await page.text_content('body')
            dados_dinamicos['full_page_text'] = page_text[:2000]  # Primeiros 2000 chars
            
            print("=" * 60)
            print("🔍 DEBUG - CONTEÚDO DA PÁGINA CAPTURADO:")
            print("=" * 60)
            print(f"📄 Primeiros 500 caracteres da página:")
            print(f"{page_text[:500]}")
            print("=" * 60)
            
            # 1. CAPTURAR NOME DO JOGADOR (GENÉRICO)
            try:
                # Capturar qualquer nome que apareça na página
                display_name = None
                
                # Procurar por padrões de nome comum
                name_patterns = [
                    r'([A-Z0-9]{2,6}\s*\|\s*[^\n\r\|]{3,25})',  # Team | Player
                    r'([A-Za-z0-9_\s]{3,30})\s*Steam',          # Nome antes de "Steam"
                    r'([A-Za-z0-9_\s]{3,30})\s*View on',        # Nome antes de "View on"
                    r'([A-Za-z0-9_\s]{3,30})\s*Current Rank',   # Nome antes de "Current Rank"
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, page_text[:1000])  # Primeiros 1000 chars
                    if match:
                        candidate = match.group(1).strip()
                        # Filtrar candidatos válidos
                        if (len(candidate) >= 3 and len(candidate) <= 30 and 
                            not candidate.isdigit() and 
                            'REMATCH' not in candidate.upper() and
                            'TRACKER' not in candidate.upper()):
                            display_name = candidate
                            break
                
                # Fallback: pegar primeiro texto "limpo" da página
                if not display_name:
                    lines = page_text[:2000].split('\n')
                    for line in lines:
                        line = line.strip()
                        if (3 <= len(line) <= 30 and 
                            not line.isdigit() and 
                            not line.startswith('http') and
                            'REMATCH' not in line.upper()):
                            display_name = line
                            break
                
                if display_name:
                    dados_dinamicos['player_info']['display_name'] = display_name
                    print(f"👤 NOME ENCONTRADO: {display_name}")
                else:
                    print("⚠️ Nome do jogador não identificado")
                    
                print(f"🔍 DEBUG NOME - Primeiros 1000 chars analisados:")
                print(f"   {page_text[:1000][:200]}...")  # Mostra 200 chars para debug
                    
            except Exception as e:
                print(f"⚠️ Erro ao capturar nome: {e}")
            
            # 2. CAPTURAR GRADE/NOTA (usando seletor HTML específico)
            try:
                grade_found = None
                
                # Primeira tentativa: buscar por TODOS os spans com classe svelte-bvxqti
                print("🔍 Buscando grade em todos os spans com classe 'svelte-bvxqti'...")
                try:
                    grade_elements = await page.query_selector_all('span.svelte-bvxqti')
                    print(f"📊 Encontrados {len(grade_elements)} spans com classe 'svelte-bvxqti'")
                    
                    for i, element in enumerate(grade_elements):
                        element_text = await element.text_content()
                        element_style = await element.get_attribute('style')
                        
                        print(f"   Span {i+1}: texto='{element_text}', style='{element_style}'")
                        
                        if element_text and element_text.strip():
                            text = element_text.strip().upper()
                            # Verificar se é uma grade válida (S+, S-, S, A+, A-, A, B+, etc.)
                            if re.match(r'^[S][+\-]?$|^[A-F][+\-]?$', text):
                                grade_found = text
                                print(f"📊 GRADE ENCONTRADA NO SPAN {i+1}: {grade_found}")
                                break
                    
                    if not grade_found:
                        print("⚠️ Nenhuma grade válida encontrada nos spans 'svelte-bvxqti'")
                except Exception as span_error:
                    print(f"⚠️ Erro ao buscar spans específicos: {span_error}")
                
                # Segunda tentativa: buscar por qualquer span que contenha grades válidas
                if not grade_found:
                    print("🔍 Buscando grade em todos os spans...")
                    try:
                        all_spans = await page.query_selector_all('span')
                        for span in all_spans:
                            span_text = await span.text_content()
                            if span_text and span_text.strip():
                                text = span_text.strip().upper()
                                # Verificar se é uma grade válida
                                if re.match(r'^[S][+\-]?$|^[A-F][+\-]?$', text):
                                    grade_found = text
                                    print(f"📊 GRADE ENCONTRADA EM SPAN GENÉRICO: {grade_found}")
                                    break
                        if not grade_found:
                            print("⚠️ Nenhuma grade válida encontrada nos spans")
                    except Exception as spans_error:
                        print(f"⚠️ Erro ao buscar spans genéricos: {spans_error}")
                
                # Terceira tentativa: buscar qualquer elemento com cor específica (fallback)
                if not grade_found:
                    print("🔍 Buscando grade por cor específica...")
                    try:
                        # Buscar elementos com cor verde específica do exemplo
                        colored_elements = await page.query_selector_all('[style*="color: rgb(58, 242, 178)"]')
                        for element in colored_elements:
                            element_text = await element.text_content()
                            if element_text and element_text.strip():
                                text = element_text.strip().upper()
                                if re.match(r'^[S][+\-]?$|^[A-F][+\-]?$', text):
                                    grade_found = text
                                    print(f"📊 GRADE ENCONTRADA POR COR: {grade_found}")
                                    break
                        if not grade_found:
                            print("⚠️ Nenhuma grade válida encontrada por cor")
                    except Exception as color_error:
                        print(f"⚠️ Erro ao buscar por cor: {color_error}")
                
                # Última tentativa: regex no texto (fallback)
                if not grade_found:
                    print("🔍 Última tentativa: regex no texto...")
                    grade_patterns = [
                        r'\b([S][+\-])\b',      # S+, S-
                        r'\b([A-F][+\-])\b',    # A+, A-, B+, B-, etc.
                        r'\b([S])\b',           # S
                        r'\b([A-F])\b',         # A, B, C, D, F
                    ]
                    
                    for pattern in grade_patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE)
                        if matches:
                            # Pegar o primeiro match válido
                            for match in matches:
                                if match and 1 <= len(match) <= 3:
                                    grade_found = match.upper()
                                    print(f"📊 GRADE ENCONTRADA POR REGEX: {grade_found}")
                                    break
                            if grade_found:
                                break
                
                if grade_found:
                    dados_dinamicos['player_info']['grade'] = grade_found
                    print(f"📊 GRADE FINAL CAPTURADA: {grade_found}")
                else:
                    print("⚠️ Grade não identificada com nenhum método")
                    # Debug: mostrar alguns spans para análise
                    try:
                        print("🔍 DEBUG - Primeiros 10 spans encontrados:")
                        debug_spans = await page.query_selector_all('span')
                        for i, span in enumerate(debug_spans[:10]):
                            span_text = await span.text_content()
                            span_html = await span.inner_html()
                            print(f"   Span {i+1}: '{span_text}' | HTML: {span_html[:50]}...")
                    except:
                        print("⚠️ Não foi possível mostrar debug dos spans")
                    
            except Exception as e:
                print(f"⚠️ Erro geral ao capturar grade: {e}")
            
            # 3. CAPTURAR TIPO DE JOGADOR (qualquer palavra + Player)
            try:
                # Buscar qualquer padrão "XXX Player"
                player_type_match = re.search(r'([A-Za-z]+\s+Player)', page_text)
                all_player_matches = re.findall(r'([A-Za-z]+\s+Player)', page_text)
                print(f"🔍 DEBUG TIPO - Padrões 'XXX Player' encontrados: {all_player_matches}")
                
                if player_type_match:
                    dados_dinamicos['player_info']['player_type'] = player_type_match.group(1)
                    print(f"🎯 TIPO ENCONTRADO: {player_type_match.group(1)}")
                else:
                    print("⚠️ Tipo de jogador não identificado")
            except Exception as e:
                print(f"⚠️ Erro ao capturar tipo: {e}")
            
            # 4. CAPTURAR RANK (qualquer palavra que pareça um rank)
            try:
                # Buscar padrões comuns de rank
                rank_patterns = [
                    r'Current Rank[:\s]*([A-Za-z]+)',
                    r'Rank[:\s]*([A-Za-z]+)',
                    r'\b(Elite|Mestre|Master|Diamante|Diamond|Platina|Platinum|Ouro|Gold|Prata|Silver|Bronze)\b'
                ]
                
                rank_found = None
                print(f"🔍 DEBUG RANK - Padrões buscados:")
                for pattern in rank_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    print(f"   Padrão '{pattern}': {matches}")
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        rank_found = match.group(1)
                        print(f"🏆 RANK ENCONTRADO: {rank_found}")
                        break
                
                if rank_found:
                    dados_dinamicos['player_info']['rank'] = rank_found
                else:
                    print("⚠️ Rank não identificado")
                    
            except Exception as e:
                print(f"⚠️ Erro ao capturar rank: {e}")
            
            # 5. CAPTURAR VALORES NUMÉRICOS (playing style, stats, etc.)
            try:
                # Capturar qualquer valor X/100 que apareça
                valores_100 = re.findall(r'(\d+)/100', page_text)
                print(f"🔍 DEBUG VALORES /100 - Encontrados: {valores_100}")
                
                if valores_100:
                    # Atribuir aos primeiros 6 valores como playing style
                    categories = ['attack', 'playmaking', 'finishing', 'defense', 'goalkeeper', 'impact']
                    for i, value in enumerate(valores_100[:6]):
                        if i < len(categories):
                            dados_dinamicos['playing_style_analysis'][categories[i]] = int(value)
                            print(f"🎮 {categories[i].title()}: {value}/100")
                        else:
                            # Valores extras vão para stats extras
                            dados_dinamicos['page_stats'][f'extra_stat_{i-5}'] = int(value)
                            print(f"📊 Extra Stat {i-5}: {value}/100")
                
                # Capturar valores percentuais adicionais
                percentuais = re.findall(r'(\d+(?:\.\d+)?)%', page_text)
                print(f"🔍 DEBUG PERCENTUAIS - Encontrados: {percentuais[:10]}")  # Primeiros 10
                
                if percentuais:
                    for i, perc in enumerate(percentuais[:5]):  # Primeiros 5 percentuais
                        dados_dinamicos['page_stats'][f'percent_{i+1}'] = float(perc)
                        print(f"📊 Percent {i+1}: {perc}%")
                
                # Capturar números grandes (com k, mil, etc.)
                numeros_grandes = re.findall(r'(\d+\.?\d*k|\d{4,})', page_text)
                print(f"🔍 DEBUG NÚMEROS GRANDES - Encontrados: {numeros_grandes[:10]}")  # Primeiros 10
                
                if numeros_grandes:
                    for i, num in enumerate(numeros_grandes[:5]):  # Primeiros 5 números grandes
                        dados_dinamicos['page_stats'][f'big_number_{i+1}'] = num
                        print(f"🔢 Número {i+1}: {num}")
                            
            except Exception as e:
                print(f"⚠️ Erro ao capturar valores: {e}")
            
            # 6. CAPTURAR ELEMENTOS DE TEXTO ADICIONAIS
            try:
                # Capturar todo texto útil em elementos pequenos
                elements_text = []
                
                # Procurar por elementos pequenos que podem conter informações úteis
                body_text_lines = page_text.split('\n')
                for line in body_text_lines:
                    line = line.strip()
                    # Capturar linhas pequenas e úteis (pode ser stats, nomes, etc.)
                    if (2 <= len(line) <= 50 and 
                        not line.startswith('http') and 
                        not line.isdigit() and
                        'javascript' not in line.lower()):
                        elements_text.append(line)
                
                # Salvar alguns elementos de texto para debug
                dados_dinamicos['raw_elements']['text_elements'] = elements_text[:20]  # Primeiros 20
                print(f"📝 ELEMENTOS DE TEXTO CAPTURADOS ({len(elements_text[:20])}):")
                for i, elemento in enumerate(elements_text[:10]):  # Mostrar primeiros 10
                    print(f"   {i+1}. {elemento}")
                if len(elements_text) > 10:
                    print(f"   ... e mais {len(elements_text) - 10} elementos")
                    
            except Exception as e:
                print(f"⚠️ Erro ao capturar elementos extras: {e}")
            
            await context.close()
            await browser.close()
            
            # LOG FINAL - RESUMO DE TUDO QUE FOI CAPTURADO
            print("=" * 60)
            print("📋 RESUMO FINAL DO SCRAPING:")
            print("=" * 60)
            print(f"🎯 Steam ID: {steam_id}")
            print(f"👤 Nome: {dados_dinamicos['player_info']['display_name']}")
            print(f"📊 Grade: {dados_dinamicos['player_info']['grade']}")
            print(f"🎯 Tipo: {dados_dinamicos['player_info']['player_type']}")
            print(f"🏆 Rank: {dados_dinamicos['player_info']['rank']}")
            print(f"🎮 Playing Style: {dados_dinamicos['playing_style_analysis']}")
            print(f"📊 Stats: {dados_dinamicos['page_stats']}")
            print(f"📝 Elementos: {len(dados_dinamicos['raw_elements']['text_elements'])} capturados")
            print("=" * 60)
            print("✅ Scraping dinâmico concluído com sucesso!")
            
            return dados_dinamicos
            
        except Exception as e:
            if 'context' in locals():
                await context.close()
            if browser:
                await browser.close()
            print(f"❌ Erro no scraping dinâmico: {e}")
            print("🔍 DEBUG ERRO - Tentando capturar conteúdo antes do erro...")
            try:
                if 'page_text' in locals() and page_text:
                    print(f"📄 Conteúdo parcial capturado: {page_text[:300]}...")
            except:
                print("⚠️ Não foi possível mostrar conteúdo parcial")
            
            return {
                'steam_id': steam_id,
                'url': url,
                'error': str(e),
                'method': 'playwright_dynamic',
                'status': 'error',
                'captured_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

def fazer_scraping_dinamico_sync(steam_id):
    """
    Versão síncrona para integrar com o Flask
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resultado = loop.run_until_complete(scraping_dinamico_rematch(steam_id))
        loop.close()
        return resultado
    except Exception as e:
        return {
            'steam_id': steam_id,
            'error': f'Erro no loop assíncrono: {e}',
            'method': 'playwright_dynamic',
            'status': 'error'
        } 