from app.db.session import SessionLocal
from app.models.prompt import Prompt, PromptVersion
from sqlalchemy import select


def seed():
    db = SessionLocal()
    try:
        # Check if greeting prompt exists
        res = db.execute(select(Prompt).where(Prompt.name == 'greeting'))
        p = res.scalars().first()
        if p:
            print('Prompt "greeting" already exists')
            return
        # Create prompt
        p = Prompt(name='greeting', description='Simple greeting prompt')
        db.add(p)
        db.commit()
        db.refresh(p)

        pv = PromptVersion(
            prompt_id=p.id,
            version='1.0.0',
            system_template=None,
            user_template='Say hello to {name} in a friendly tone.',
            model_config={"provider": "mock", "model": "mock-model", "temperature": 0.3},
            author='seed',
            is_active=True,
        )
        db.add(pv)
        db.commit()
        print('Seeded prompt greeting v1.0.0')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
