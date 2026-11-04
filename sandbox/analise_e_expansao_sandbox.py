# -*- coding: utf-8 -*-
"""
Motor Filológico e Gerador de Sandbox da Língua Tréppia (Era Clássica V8.1)
Verifica leis fonotáticas, sandi consonantal, haplologia apostrófica e gera
o Compêndio de Expansão Naturalista em Sandbox.
"""

import os
import json

# 1. Raízes Verbais Atestadas no Corpus Oficial (Gramática Normativa + V8.1)
RAIZES_VERBAIS_ATESTADAS = [
    # (raiz_positiva, glosa_pos, glosa_priv, glosa_iter, glosa_iter_priv, notas_fonotaticas)
    ("bar", "irritar, provocar", "apaziguar, acalmar a ira", "voltar a irritar", "voltar a apaziguar", "r+ra/ru -> rra/rru (barram/barrum)"),
    ("dak", "flanquear à direita, ordenar", "desalinhar o flanco direito", "reordenar à direita", "voltar a desalinhar à direita", "kb -> bb no imperfeito (dabbam; hist. dagbam); od-a-dak- -> oda'ak- (haplologia dental d-d)"),
    ("doot", "entediar-se, estagnar no ócio", "estimular, despertar do tédio", "voltar a entediar-se", "voltar a despertar do tédio", "tb -> bb no imperfeito (doobbam); od-a-doot- -> oda'oot- (haplologia dental d-d)"),
    ("dur", "brilhar, resplandecer", "obscurecer, apagar o brilho", "voltar a brilhar, reacender", "voltar a obscurecer", "r+ra/ru -> rra/rru (durram/durrum); od-a-dur- -> oda'ur- (haplologia canônica)"),
    ("elf", "sacralizar, santificar", "profanar, dessacralizar", "ressacralizar, consagrar de novo", "voltar a profanar", "fb -> bb no imperfeito (elbbam / aelbbam)"),
    ("es", "ser, estar, existir", "deixar de ser, inexistir", "restituir o estado, voltar a ser", "voltar a deixar de ser", "sr -> ss no passado/futuro (essa/essu, aessam); vogal inicial exige od- (odesur, od-a-es- -> odaes-)"),
    ("fas", "padecer, sofrer dor", "aliviar a dor, consolar", "voltar a padecer", "voltar a aliviar a dor", "sr -> ss no passado/futuro (fassa/fassu)"),
    ("gald", "guardar, carregar, custodiar", "abandonar custódia, desguarnecer", "re-guardar, reassumir guarda", "voltar a abandonar a guarda", "ldb -> lbb no imperfeito (galbbam / agalbbam)"),
    ("galdex", "sacar, desembainhar", "reembainhar, recolher lâmina", "voltar a desembainhar", "voltar a reembainhar", "xr -> rr no passado/futuro (galderra / agalderra)"),
    ("gel", "transladar, levar, conduzir", "reter, impedir translado", "retransladar, reconduzir", "voltar a reter", " líquida lateral estável"),
    ("gir", "crescer, expandir-se", "diminuir, minguar, encolher", "voltar a crescer", "voltar a diminuir", "r+ra/ru -> rra/rru (girram/girrum)"),
    ("giz", "amar, recordar com devoção", "odiar, esquecer cognitivamente", "voltar a amar", "voltar a odiar ou esquecer", "zr -> zz no passado/futuro (gizza / agizza)"),
    ("illot", "embelezar, adornar (in+lota)", "desadornar, despojar de beleza", "readornar, voltar a embelezar", "voltar a desadornar", "nl -> ll na origem; tb -> bb no imperfeito (illobbam); vogal inicial exige od- (odillotur)"),
    ("intul", "enlouquecer, delirar (in+tul)", "recobrar a razão, sanar a mente", "voltar a enlouquecer", "voltar a recobrar a razão", "vogal inicial exige od- (odintulur)"),
    ("kam", "embriagar, entorpecer", "desembriagar, tornar sóbrio", "voltar a embriagar", "voltar a tornar sóbrio", "mr -> mm no passado/futuro (kamma/kammu)"),
    ("kaz", "viver, existir em carne", "perecer, morrer, falecer", "ressuscitar, renascer", "voltar a perecer", "zr -> zz no passado/futuro (kazza / akazza / okazza)"),
    ("kel", "mover em conjunto, manobrar", "imobilizar, dispersar formação", "reagrupar em marcha", "voltar a imobilizar", "raiz motora tática primária"),
    ("kelad", "aproximar-se, advir (kel+ad)", "afastar-se, retirar-se", "reaproximar-se, retornar", "voltar a afastar-se", "dental final (keladuke; imperf. kelabbam por db/tb Assimilação)"),
    ("kelex", "escapar, evadir-se (kel+ex)", "ficar preso, estagnar", "voltar a escapar", "voltar a ficar preso", "xr -> rr no passado/futuro (kelerra / akelerra)"),
    ("kel'un", "escoltar, proteger em marcha", "abandonar escolta, desproteger comboio", "reescoltar", "voltar a abandonar escolta", "haplologia velar kel+kun; nr -> nn (akel'unnam); nb -> mb (kel'umbam)"),
    ("kit", "escrever, lavrar em registro", "perdoar institucionalmente, rasurar dívida", "reescrever, relavrar", "voltar a rasurar ou perdoar", "tb -> bb no imperfeito (kibbam / akibbam)"),
    ("kom", "beber, sorver", "privar de fluidos, dar sede", "voltar a beber", "voltar a dar sede", "mr -> mm no passado/futuro (komma / akommam)"),
    ("kos", "esconder, sepultar, ocultar", "expor, desvelar, exumar", "reesconder, voltar a ocultar", "voltar a expor", "sr -> ss no passado/futuro (kossa/kossu)"),
    ("krad", "criar, fundar, erigir", "destruir, descriar, demolir", "recriar, refundar", "voltar a destruir", "dt -> tt em agente (Kratte)"),
    ("lakanav", "amaldiçoar, imprecar (laka+nav)", "suspender maldição, expiar", "voltar a amaldiçoar", "voltar a suspender maldição", "composto verbal com nav-"),
    ("lan", "emanar luz, iluminar", "obliterar a luz, apagar", "reiluminar, voltar a brilhar", "voltar a obliterar a luz", "nr -> nn no passado/futuro (lannam); nb -> mb no imperfeito (lambam / alambam)"),
    ("let", "falar, enunciar, proferir", "silenciar violentamente, calar", "reiterar a fala, repetir", "voltar a silenciar", "tb -> bb no imperfeito (lebbam / alebbam)"),
    ("litr", "vibrar, ressoar", "amortecer, cessar vibração", "voltar a vibrar", "voltar a amortecer", "r+ra/ru -> rra/rru (litrram/litrrum)"),
    ("mak", "comer, alimentar-se", "esfomear, privar de alimento", "voltar a comer", "voltar a esfomear", "kb -> bb no imperfeito (mabbam / amabbam; hist. magbam/amagbam)"),
    ("met", "glorificar, exaltar", "humilhar, rebaixar a honra", "voltar a glorificar", "voltar a humilhar", "tb -> bb no imperfeito (mebbam)"),
    ("mir", "ver, vigiar, contemplar", "cegar, privar de visão", "rever, tornar a vigiar", "voltar a cegar", "r+ra/ru -> rra/rru (mirram/mirrum, amirram/amirrum)"),
    ("mob", "beneficiar, dar, conceder", "privar de benefício, confiscar", "restituir dádiva, voltar a dar", "voltar a confiscar", "imperativo puro Mob!"),
    ("mobanav", "bendizer, abençoar (moban+nav)", "retirar bênção, desconsagrar", "reabençoar", "voltar a retirar bênção", "particípio mobanavet"),
    ("mollet", "julgar, sentenciar (mon+let)", "absolver sem juízo, revogar sentença", "rejulgar, revisar processo", "voltar a revogar sentença", "nl -> ll na origem; tb -> bb no imperfeito (mollebbam)"),
    ("nav", "transformar, tornar-se, converter", "estabilizar, impedir mutação", "retransformar, reconverter", "voltar a impedir mutação", "vt -> pt se afixado com -ta"),
    ("par", "merecer, ser digno de", "desmerecer, perder a dignidade", "voltar a merecer", "voltar a desmerecer", "r+ra/ru -> rra/rru (parram/parrum)"),
    ("pas", "precisar, necessitar, carecer", "bastar-se, prescindir", "voltar a precisar", "voltar a prescindir", "sr -> ss no passado/futuro (passa/passu)"),
    ("said", "afiar, amolar lâmina", "embotar, cegar o fio da lâmina", "reafiar, tornar a amolar", "voltar a embotar", "dt -> tt em derivados com -te/-tek"),
    ("sfar", "proteger, defender, livrar", "aniquilar, exterminar, desproteger", "voltar a proteger", "voltar a aniquilar", "r+ra/ru -> rra/rru (sfarram/sfarrum, asfarram/asfarrum)"),
    ("sif", "contar histórias, narrar crônica", "omitir dos anais, apagar relato", "recontar, reiterar crônica", "voltar a omitir dos anais", "fb -> bb no imperfeito (sibbam)"),
    ("sin", "flanquear à esquerda", "desguarnecer a esquerda", "reordenar à esquerda", "voltar a desguarnecer a esquerda", "nr -> nn no passado/futuro (sinnam); nb -> mb no imperfeito (simbam)"),
    ("skor", "crer, professar fé", "descrer, apostatar", "voltar a crer, reconverter-se", "voltar a descrer", "r+ra/ru -> rra/rru (skorram/skorrum)"),
    ("tek", "fazer, fabricar, realizar", "desfazer, desmontar obra", "refazer, reconstruir", "voltar a desfazer", "kb -> bb no imperfeito V8.1 (tebbam; base normativa registra tekbam)"),
    ("tok", "governar, reger com soberania", "desgovernar, subverter a ordem", "voltar a governar", "voltar a desgovernar", "kb -> bb no imperfeito (tobbam / atobbam; hist. togbam)"),
    ("tol", "formar beleza, modelar (de tola)", "desfigurar, deformar (atolur)", "remodelar, restaurar feição", "voltar a desfigurar", "ln -> ll se acrescido de -n"),
    ("tor", "possuir, deter pela força", "desapossar, perder domínio", "reaver posse, reconquistar", "voltar a desapossar", "r+ra/ru -> rra/rru (torram/torrum)"),
    ("torex", "tomar à força, arrebatar (tor+ex)", "restituir à força, devolver presa", "voltar a tomar à força", "voltar a restituir à força", "xr -> rr no passado/futuro (torerra / atorerra)"),
    ("trak", "marchar, avançar em comando", "retrair, deter marcha", "recuar vanguarda, retroceder", "voltar a retrair", "kt -> tt em agente (Trátte); kb -> bb no imperfeito (trabbam; hist. tragbam)"),
    ("yn", "andar, caminhar, prosseguir", "estancar o passo, deter-se", "voltar a caminhar, prosseguir", "voltar a estancar o passo", "nr -> nn no passado/futuro (ynna/ynnu); nb -> mb no imperfeito (ymbam); vogal inicial exige od- (odynur)")
]

print(f"Total de grupos verbais nucleares catalogados para análise: {len(RAIZES_VERBAIS_ATESTADAS)}")

