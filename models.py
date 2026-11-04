"""Die 16 Tabellen. Schlüssel und Pflichtfelder werden in der Datenbank geprüft."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Boolean, CHAR, CheckConstraint, Date, DateTime, ForeignKey,
    Identity, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


def identity_pk():
    # Automatische ID; die INTEGER-Variante erlaubt lokale Prüfungen mit SQLite.
    return mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), Identity(), primary_key=True
    )


class Paciente(Base):
    __tablename__ = "paciente"
    __table_args__ = (
        CheckConstraint("length(cpf) = 11", name="cpf_tamanho"),
        CheckConstraint("faixa_renda_familiar >= 0", name="renda_nao_negativa"),
    )

    cpf: Mapped[str] = mapped_column(CHAR(11), primary_key=True)
    rg: Mapped[str | None] = mapped_column(String(20), unique=True)
    numero_cartao_sus: Mapped[str | None] = mapped_column(CHAR(15), unique=True)
    nome_completo: Mapped[str] = mapped_column(String(150))
    data_nascimento: Mapped[date] = mapped_column(Date)
    sexo_biologico: Mapped[str] = mapped_column(String(20))
    genero: Mapped[str | None] = mapped_column(String(50))
    telefone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    logradouro: Mapped[str] = mapped_column(String(150))
    numero_endereco: Mapped[str] = mapped_column(String(20))
    complemento: Mapped[str | None] = mapped_column(String(100))
    bairro: Mapped[str] = mapped_column(String(100))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(CHAR(2))
    cep: Mapped[str] = mapped_column(CHAR(8))
    raca_cor: Mapped[str | None] = mapped_column(String(50))
    estado_civil: Mapped[str | None] = mapped_column(String(30))
    escolaridade: Mapped[str | None] = mapped_column(String(60))
    ocupacao: Mapped[str | None] = mapped_column(String(100))
    faixa_renda_familiar: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    possui_plano_saude: Mapped[bool] = mapped_column(Boolean)
    operadora_plano_saude: Mapped[str | None] = mapped_column(String(100))
    contato_emergencia_nome: Mapped[str | None] = mapped_column(String(150))
    contato_emergencia_telefone: Mapped[str | None] = mapped_column(String(20))
    contato_emergencia_relacao: Mapped[str | None] = mapped_column(String(60))


class Atendente(Base):
    __tablename__ = "atendente"
    __table_args__ = (CheckConstraint("length(cpf) = 11", name="cpf_tamanho"),)

    cpf: Mapped[str] = mapped_column(CHAR(11), primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String(150))
    telefone: Mapped[str] = mapped_column(String(20))


class ProfissionalSaude(Base):
    __tablename__ = "profissional_saude"

    cpf: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("atendente.cpf", ondelete="RESTRICT"), primary_key=True
    )
    numero_profissional: Mapped[str] = mapped_column(String(30), unique=True)
    conselho_registro: Mapped[str] = mapped_column(String(20), unique=True)
    especialidade_area: Mapped[str] = mapped_column(String(100))
    instituicao_vinculo: Mapped[str | None] = mapped_column(String(150))


class Estagiario(Base):
    __tablename__ = "estagiario"

    cpf: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("atendente.cpf", ondelete="RESTRICT"), primary_key=True
    )
    instituicao_ensino: Mapped[str] = mapped_column(String(150))
    curso_formacao: Mapped[str] = mapped_column(String(100))


class EstabelecimentoSaude(Base):
    __tablename__ = "estabelecimento_saude"

    id_estabelecimento: Mapped[int] = identity_pk()
    nome: Mapped[str] = mapped_column(String(150))
    tipo_atendimento: Mapped[str] = mapped_column(String(80))
    cep: Mapped[str] = mapped_column(CHAR(8))
    logradouro: Mapped[str] = mapped_column(String(150))
    numero_endereco: Mapped[str] = mapped_column(String(20))
    complemento: Mapped[str | None] = mapped_column(String(100))
    bairro: Mapped[str] = mapped_column(String(100))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(CHAR(2))


class Medicamento(Base):
    __tablename__ = "medicamento"

    id_medicamento: Mapped[int] = identity_pk()
    nome: Mapped[str] = mapped_column(String(150))


class CondicaoSaude(Base):
    __tablename__ = "condicao_saude"

    id_condicao: Mapped[int] = identity_pk()
    nome: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str] = mapped_column(String(60))


class TipoParametro(Base):
    __tablename__ = "tipo_parametro"

    id_tipo_parametro: Mapped[int] = identity_pk()
    nome: Mapped[str] = mapped_column(String(100))
    unidade_medida: Mapped[str] = mapped_column(String(30))
    faixa_referencia: Mapped[str | None] = mapped_column(Text)


class Consulta(Base):
    __tablename__ = "consulta"

    id_consulta: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    cpf_profissional_responsavel: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("profissional_saude.cpf", ondelete="RESTRICT"), index=True
    )
    cpf_estagiario: Mapped[str | None] = mapped_column(
        CHAR(11), ForeignKey("estagiario.cpf", ondelete="RESTRICT"), index=True
    )
    id_estabelecimento: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("estabelecimento_saude.id_estabelecimento", ondelete="RESTRICT"),
        index=True,
    )
    data_realizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    especialidade_medica: Mapped[str] = mapped_column(String(100))


class AgendamentoMedicao(Base):
    __tablename__ = "agendamento_medicao"

    id_agendamento: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    cpf_profissional: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("profissional_saude.cpf", ondelete="RESTRICT"), index=True
    )
    data_horario: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20))
    observacoes: Mapped[str | None] = mapped_column(Text)


class AgendamentoParametro(Base):
    __tablename__ = "agendamento_parametro"

    id_agendamento: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("agendamento_medicao.id_agendamento", ondelete="RESTRICT"),
        primary_key=True,
    )
    id_tipo_parametro: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tipo_parametro.id_tipo_parametro", ondelete="RESTRICT"),
        primary_key=True, index=True,
    )


class MedicaoClinica(Base):
    __tablename__ = "medicao_clinica"

    id_medicao: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    id_tipo_parametro: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tipo_parametro.id_tipo_parametro", ondelete="RESTRICT"),
        index=True,
    )
    id_agendamento: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("agendamento_medicao.id_agendamento", ondelete="RESTRICT"),
        index=True,
    )
    id_consulta: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("consulta.id_consulta", ondelete="RESTRICT"), index=True
    )
    data_horario: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valor_aferido: Mapped[str] = mapped_column(String(50))
    origem: Mapped[str] = mapped_column(String(20))
    observacoes: Mapped[str | None] = mapped_column(Text)


class ResultadoExame(Base):
    __tablename__ = "resultado_exame"

    id_resultado: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    laudo_resultado: Mapped[str] = mapped_column(Text)


class PacienteCondicao(Base):
    __tablename__ = "paciente_condicao"
    __table_args__ = (
        UniqueConstraint("cpf_paciente", "id_condicao", name="uq_paciente_condicao_par"),
    )

    id_paciente_condicao: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    id_condicao: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("condicao_saude.id_condicao", ondelete="RESTRICT"), index=True
    )
    data_sintomas_ou_diagnostico: Mapped[date | None] = mapped_column(Date)


class UsoMedicamento(Base):
    __tablename__ = "uso_medicamento"
    __table_args__ = (
        CheckConstraint("data_fim IS NULL OR data_fim >= data_inicio", name="ordem_datas"),
    )

    id_uso_medicamento: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    id_medicamento: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("medicamento.id_medicamento", ondelete="RESTRICT"), index=True
    )
    dose: Mapped[str] = mapped_column(String(50))
    frequencia: Mapped[str] = mapped_column(String(80))
    forma_farmaceutica: Mapped[str] = mapped_column(String(60))
    via_administracao: Mapped[str] = mapped_column(String(60))
    data_inicio: Mapped[date] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    foi_prescrito: Mapped[bool] = mapped_column(Boolean)
    instrucoes: Mapped[str | None] = mapped_column(Text)


class ReacaoAlergica(Base):
    __tablename__ = "reacao_alergica"

    id_reacao: Mapped[int] = identity_pk()
    cpf_paciente: Mapped[str] = mapped_column(
        CHAR(11), ForeignKey("paciente.cpf", ondelete="RESTRICT"), index=True
    )
    id_medicamento: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("medicamento.id_medicamento", ondelete="RESTRICT"), index=True
    )
    data_ocorrencia: Mapped[date | None] = mapped_column(Date)
    descricao: Mapped[str] = mapped_column(Text)
