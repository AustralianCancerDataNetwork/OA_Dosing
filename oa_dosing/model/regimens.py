from datetime import datetime, date
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from omop_alchemy.db import Base

# custom study-specific tables

class Drug_Context(Base):
    __tablename__ = 'drug_context'
    # identifier
    drug_context_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    # concept fks
    drug_concept_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('concept.concept_id'))
    diagnosis_concept_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('concept.concept_id'))    
    # concept relationships
    drug_concept: so.Mapped['Concept'] = so.relationship(foreign_keys=[drug_concept_id])
    diagnosis_concept: so.Mapped['Concept'] = so.relationship(foreign_keys=[diagnosis_concept_id])

class Regimen_Reference(Base):
    __tablename__ = 'regimen_reference'
    # identifier
    regimen_reference_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    # strings
    regimen_reference_name: so.Mapped[str] = so.mapped_column(sa.String(250))
    regimen_label: so.Mapped[str] = so.mapped_column(sa.String(250))
    common_name: so.Mapped[str] = so.mapped_column(sa.String(250))
    context: so.Mapped[str] = so.mapped_column(sa.String(250))
    variant_descriptor: so.Mapped[Optional[str]] = so.mapped_column(sa.String(250), nullable=True)
    # fks
    variant_of_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('regimen_reference.regimen_reference_id'), nullable=True)
    # concept fks
    hemonc_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('concept.concept_id'), nullable=True)
    # relationships
    variant_of: so.Mapped[Optional['Regimen_Reference']] = so.relationship(foreign_keys=[variant_of_id], remote_side=regimen_reference_id)
    has_variants: so.Mapped[List['Regimen_Reference']] = so.relationship(back_populates="variant_of", lazy="selectin")
    has_context: so.Mapped['Regimen_Context'] = so.relationship(back_populates="context_of", lazy="selectin")
    has_parts: so.Mapped[List['Regimen_Part']] = so.relationship(back_populates="part_of_regimen", lazy="selectin")
    # concept relationships
    hemonc_concept: so.Mapped[Optional['Concept']] = so.relationship(foreign_keys=[hemonc_id])

class Regimen_Multiples(Base):
    __tablename__ = 'regimen_multiples'
    regimen_reference_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('regimen_reference.regimen_reference_id'), primary_key=True, autoincrement=True)
    equivalent_regimen_reference_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('regimen_reference.regimen_reference_id'),primary_key=True, autoincrement=True)

class Regimen_Context(Base):
    __tablename__ = 'regimen_context'
    # identifier
    regimen_context_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    # fks
    regimen_reference_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('regimen_reference.regimen_reference_id'))
    # concept fks
    diagnosis_concept_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('concept.concept_id')) 
    # relationships
    context_of: so.Mapped['Regimen_Reference'] = so.relationship(foreign_keys=[regimen_reference_id])
    # concept relationships
    diagnosis_concept: so.Mapped['Concept'] = so.relationship(foreign_keys=[diagnosis_concept_id])

class Regimen_Part(Base):
    __tablename__ = 'regimen_part'
    # identifier
    regimen_part_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    # fks
    part_of: so.Mapped[int] = so.mapped_column(sa.ForeignKey('regimen_reference.regimen_reference_id'))
    # numeric
    path: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    part: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    # strings
    branch: so.Mapped[Optional[str]] = so.mapped_column(sa.String(250), nullable=True)
    # relationships
    part_of_regimen: so.Mapped[List['Regimen_Reference']] = so.relationship(foreign_keys=[part_of])
    has_cycles: so.Mapped[List['Cycle_Reference']] = so.relationship(back_populates="cycle_of", lazy="selectin")


class Cycle_Reference(Base):
    __tablename__ = 'cycle_reference'

    # identifier
    cycle_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    # fks
    regimen_part: so.Mapped[int] = so.mapped_column(sa.ForeignKey('regimen_part.regimen_part_id'))
    # numeric
    cycle_number: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    cycle_length: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    min_cycles: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    max_cycles: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    # relationships
    cycle_of: so.Mapped[Optional['Regimen_Part']] = so.relationship(foreign_keys=[regimen_part])
    has_drugs: so.Mapped[List['Cycle_Drug']] = so.relationship(back_populates="drug_of", lazy="selectin")


class Cycle_Drug(Base):
    __tablename__ = 'cycle_drug'
    
    # identifier
    cycle_drug_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)

    # fks
    cycle_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('cycle_reference.cycle_id'))

    # concept fks
    drug_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('concept.concept_id'))
    route_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('concept.concept_id'))
    # relationships
    drug_of: so.Mapped[Optional['Cycle_Reference']] = so.relationship(foreign_keys=[cycle_id])
    # concept relationships
    drug_concept: so.Mapped['Concept'] = so.relationship(foreign_keys=[drug_id])
    route_concept: so.Mapped['Concept'] = so.relationship(foreign_keys=[route_id])
    has_days: so.Mapped[List['Cycle_Drug_Day']] = so.relationship(back_populates="cycle_drug_day_of", lazy="selectin")


class Cycle_Drug_Day(Base):
    # TODO: consider if this is better done as relationship between cycle - day - drug
    # instead of of cycle - drug - drug day?
    __tablename__ = 'cycle_drug_day'

    # identifier
    cycle_drug_day_id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)

    # fks
    cycle_drug_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('cycle_drug.cycle_drug_id'))

    # numeric
    day: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)

    # relationships
    cycle_drug_day_of: so.Mapped[Optional['Cycle_Drug']] = so.relationship(foreign_keys=[cycle_drug_id])
